import logging
import json
from typing import Callable
from transaction import begin, commit
import sqlalchemy

from caerp_base.models.base import DBSESSION


logger = logging.getLogger(__name__)

# From https://public.opendatasoft.com/explore/dataset/codes-nsf
NSF_CODES = """[{"datasetid": "codes-nsf", "recordid": "7d59e538ad770fce77d8dd767daf4b1f4fcaeab4", "fields": {"formation": "Formations g\\u00e9n\\u00e9rales", "code_nsf": "100"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "2ba485e2d91ed18c30146df43023a3bd915af7dd", "fields": {"formation": "Math\\u00e9matiques", "code_nsf": "114"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "03d20133740320674f5c87b05a578dfae047c874", "fields": {"formation": "Sciences de la terre", "code_nsf": "117"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "b0791523793fb246d0094a91ed77dbcd9ef7d2cc", "fields": {"formation": "Histoire", "code_nsf": "126"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "a788c17800ad51d4af1e7f5645ddc8924392913f", "fields": {"formation": "Droit, sciences politiques", "code_nsf": "128"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "701cb27962fb21e442c505c7a6d1772b23337973", "fields": {"formation": "D\\u00e9veloppement des capacit\\u00e9s mentales et apprentissages de base", "code_nsf": "412"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "c385280764ccaa793b0e82c01bf0da1677cb30d0", "fields": {"formation": "Am\\u00e9nagement paysager (parcs, jardins, espaces verts ...)", "code_nsf": "214"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "8d3780e9b81fee822f483cf1477b79394e9c85e1", "fields": {"formation": "Sp\\u00e9cialit\\u00e9s pluritechnologiques, g\\u00e9nie civil, construction, bois", "code_nsf": "230"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "5d8eb717017060a36ebfcc56c885de7268d643e5", "fields": {"formation": "D\\u00e9veloppement des capacit\\u00e9s individuelles d'organisation", "code_nsf": "414"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "4f2696964bf5f8656cb17fd86ff0c7c957a807c2", "fields": {"formation": "Jeux et activit\\u00e9s sp\\u00e9cifiques de loisirs", "code_nsf": "421"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "e76d2d5f6c4c67630c24bccf7e7503200839e3bb", "fields": {"formation": "Technologies de commandes des transformations industriels (automatismes et robotique industriels, informatique industrielle)", "code_nsf": "201"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "807e07d3f1e4fce53a1f1d7a458345896dc814ce", "fields": {"formation": "Transformations chimiques et apparent\\u00e9es (y compris industrie pharmaceutique)", "code_nsf": "222"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "38cc959d40da2646aa3b4f052e46d5a455ad9dfc", "fields": {"formation": "M\\u00e9tallurgie (y compris sid\\u00e9rurgie, fonderie, non ferreux...)", "code_nsf": "223"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "99527c8e45a852024f6b2b590e196e8a7ebf7ff4", "fields": {"formation": "Sp\\u00e9cialit\\u00e9s pluritechnologiques mat\\u00e9riaux souples", "code_nsf": "240"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "5eedd0661e6908dee3c41ff0cd55a3d123af5c77", "fields": {"formation": "Sp\\u00e9cialit\\u00e9s plurivalentes sanitaires et sociales", "code_nsf": "330"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "fdd36680ce4f06b3c7eeb59f0c7b76d40def9fbe", "fields": {"formation": "Sp\\u00e9cialit\\u00e9s pluriscientifiques", "code_nsf": "110"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "2d494663fe92f1879d9282e94c0d8cdad0616662", "fields": {"formation": "Sp\\u00e9cialit\\u00e9s pluritechnologiques m\\u00e9canique-\\u00e9lectricit\\u00e9 (y compris maintenance m\\u00e9cano-\\u00e9lectrique)", "code_nsf": "250"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "543c845cee48dbaacb4f45b214e3a4858feee6d9", "fields": {"formation": "Comptabilit\\u00e9, gestion", "code_nsf": "314"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "ef3165d1fb942f7295336570789aa9a5fd2a9972", "fields": {"formation": "Informatique, traitement de l'information, r\\u00e9seaux de transmission des donn\\u00e9es", "code_nsf": "326"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "2bf443c9ebae77d9ed6efd45ebd7897d750efc1b", "fields": {"formation": "Fran\\u00e7ais, litt\\u00e9rature et civilisation fran\\u00e7aise", "code_nsf": "131"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "ce992a2a13f20786f494dc2e7de9be5e0825d790", "fields": {"formation": "Autres disciplines artistiques et sp\\u00e9cialit\\u00e9s artistiques plurivalentes", "code_nsf": "134"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "30dbe8287bbc3774c77c455b9fd901b1a8fc5f92", "fields": {"formation": "Langues vivantes, civilisations \\u00e9trang\\u00e8res et r\\u00e9gionales", "code_nsf": "136"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "612157cfd5de1e5fbc5cb1de8c4bfa11703a703a", "fields": {"formation": "Transports, manutention, magasinage", "code_nsf": "311"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "5187543d530ab431009cfd725a40b833b06d0be7", "fields": {"formation": "Finances, banque, assurances", "code_nsf": "313"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "b7331cc228ef5d4baee5671fca4fd94571963f48", "fields": {"formation": "Electricit\\u00e9, \\u00e9lectronique (non compris automatismes, productique)", "code_nsf": "255"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "7b485e8c3853c7f348c925c99357cb3cf46dcfa8", "fields": {"formation": "Techniques de l'image et du son, m\\u00e9tiers connexes du spectacle", "code_nsf": "323"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "2b838e6cf33ac39318facdfd427395c1252b2bce", "fields": {"formation": "Application des droits et statut des personnes", "code_nsf": "345"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "ab64bf1d241af1e351f0490f6942746f0502d7f4", "fields": {"formation": "D\\u00e9veloppement des capacit\\u00e9s comportementales et relationnelles", "code_nsf": "413"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "dae4b573b2e11dc4c22186b9e004101d1c7c7c2b", "fields": {"formation": "Psychologie", "code_nsf": "124"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "b28430c484e21d2d35cb70109272e480fe35c063", "fields": {"formation": "Linguistique", "code_nsf": "125"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "05ff65948c53f101bdc0775580af3518fa9046ee", "fields": {"formation": "Musique, arts du spectacle", "code_nsf": "133"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "a16e0b7e1d8c5b61fbc3c53285a1db8f7236b957", "fields": {"formation": "Sciences sociales (y compris d\\u00e9mographie, anthropologie)", "code_nsf": "123"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "b7a37b60e24ac79dff5ef5a19b73ec6fcbe36ade", "fields": {"formation": "Commerce, vente", "code_nsf": "312"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "e037d8904e4278bd0e9f150518ebc66e63aa6dd0", "fields": {"formation": "Sp\\u00e9cialit\\u00e9s plurivalentes de la communication", "code_nsf": "320"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "1cfcc7aceed33e1e7bb3afada6ba7a6949834cb4", "fields": {"formation": "Sant\\u00e9", "code_nsf": "331"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "f1c067956838d9b7e0bac9b4c98ead786fa07a6a", "fields": {"formation": "Sp\\u00e9cialit\\u00e9s plurivalentes des \\u00e9changes et de la gestion (y compris administration g\\u00e9n\\u00e9rale des entreprises et des collectivit\\u00e9s)", "code_nsf": "310"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "a9f49c2bcaedb20ba7f8e8a7396843646e0b8b60", "fields": {"formation": "Sp\\u00e9cialit\\u00e9s pluridisciplinaires, sciences humaines et droit", "code_nsf": "120"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "76ae66fb0efdf2767bd2ae0499d69ae002b01bce", "fields": {"formation": "For\\u00eats, espaces naturels, faune sauvage, p\\u00eache", "code_nsf": "213"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "9bc4a3ecc019e05b2f9b83a98ccf37a8a0a25966", "fields": {"formation": "Techniques de l'imprimerie et de l'\\u00e9dition", "code_nsf": "322"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "d2f2cb6ae8826199c8d49bdd9569c0c31756c84d", "fields": {"formation": "Secr\\u00e9tariat, bureautique", "code_nsf": "324"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "fdb3707a96b3f625a67ef53c22750ac42660e9f3", "fields": {"formation": "Enseignement, formation", "code_nsf": "333"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "6d7b684cd6758536e55a4774d85c770b4b71ed80", "fields": {"formation": "Langues et civilisations anciennes", "code_nsf": "135"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "f30e127ab60a17dcd7c6dbb3f29bd6c94a2d35cf", "fields": {"formation": "Protection et d\\u00e9veloppement du patrimoine", "code_nsf": "342"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "e6af89d50cd7691cdb1bf337cff385797ab6d60d", "fields": {"formation": "Productions animales, \\u00e9levage sp\\u00e9cialis\\u00e9, aquaculture, soins aux animaux, y compris v\\u00e9t\\u00e9rinaire", "code_nsf": "212"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "c33a096e15c13aea4e75e9fd22d81014fc28f5cf", "fields": {"formation": "B\\u00e2timent : construction et couverture", "code_nsf": "232"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "8039317a718eaa6fd3af7b08cbbddb014055ba8a", "fields": {"formation": "Habillement (y compris mode, couture)", "code_nsf": "242"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "6a215664b45dc015f78dd914f456f70bb3ec5e6e", "fields": {"formation": "Cuirs et peaux", "code_nsf": "243"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "903f6b502400662cd185af08a28ff6deaeb01bd7", "fields": {"formation": "Plasturgie, mat\\u00e9riaux composites", "code_nsf": "225"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "819802fcbcdad14d181d8df1b7b0a9968ed119f8", "fields": {"formation": "Moteurs et m\\u00e9canique auto", "code_nsf": "252"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "d951c5801d573f20889b8b8ebeebb62f68a764be", "fields": {"formation": "Physique", "code_nsf": "115"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "5e4efa6caf6b4fa7689447ccc2cebe9117acd1c2", "fields": {"formation": "Productions v\\u00e9g\\u00e9tales, cultures sp\\u00e9cialis\\u00e9es (horticulture, viticulture, arboriculture fruiti\\u00e8re...)", "code_nsf": "211"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "83cdd0aed6aa42c977792937e0dc121b96b3773f", "fields": {"formation": "Sp\\u00e9cialit\\u00e9s pluritechnologiques des transformations", "code_nsf": "220"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "aa927271e434116e2c1e5f2b5715b1cd29311b2c", "fields": {"formation": "Papier, carton", "code_nsf": "226"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "00ef3b531351fe1f0d46305504b58c89ae25aef1", "fields": {"formation": "Mines et carri\\u00e8res, g\\u00e9nie civil, topographie", "code_nsf": "231"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "dfb0983e00f0b835e07b56aded0e61030cf32454", "fields": {"formation": "Sp\\u00e9cialit\\u00e9s plurivalentes des services", "code_nsf": "300"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "7cf386453912ce127255f940ba76ef48c72fe328", "fields": {"formation": "Technologies industrielles fondamentales (g\\u00e9nie industriel, proc\\u00e9d\\u00e9s de transformation, sp\\u00e9cialit\\u00e9s \\u00e0 dominante fonctionnelle)", "code_nsf": "200"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "4ee65b8a7d3083799b5079da6797deb60da157f5", "fields": {"formation": "Textile", "code_nsf": "241"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "f4ab70778a3b8241b9a813ee27764ac3c9dbdbec", "fields": {"formation": "Chimie-biologie, biochimie", "code_nsf": "112"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "c02a26ee7273464c8be9fa938edb9c93b67e23a6", "fields": {"formation": "Sciences naturelles (biologie-g\\u00e9ologie)", "code_nsf": "113"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "fb858171f5cd3eeb29944e6fcd4bc385ce5c7a92", "fields": {"formation": "Mat\\u00e9riaux de construction, verre, c\\u00e9ramique", "code_nsf": "224"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "1c542a0f2765e2bf6e198dc7508aa0a651d4cc7f", "fields": {"formation": "B\\u00e2timent : finitions", "code_nsf": "233"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "b04ed38273056513cc5add19a7e2f2d697e8b7ca", "fields": {"formation": "Animation culturelle, sportive et de loisirs", "code_nsf": "335"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "67814f670727b3eec23b202cf03efbfe8054fa20", "fields": {"formation": "Sp\\u00e9cialit\\u00e9s litt\\u00e9raires et artistiques plurivalentes", "code_nsf": "130"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "73ada252237dbf0ba33e625bc7f24f74b6e54bad", "fields": {"formation": "M\\u00e9canique g\\u00e9n\\u00e9rale et de pr\\u00e9cision, usinage", "code_nsf": "251"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "46b745319358addfe34d894e2c0594a28753ac61", "fields": {"formation": "Travail social", "code_nsf": "332"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "2cb1634d4ff64c3d69e757b4995e7b1024b70c1c", "fields": {"formation": "Coiffure, esth\\u00e9tique et autres sp\\u00e9cialit\\u00e9s des services aux personnes", "code_nsf": "336"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "9aee9600685fb51bd636cc0690a030d6d2a50e4d", "fields": {"formation": "Pratiques sportives (y compris : arts martiaux)", "code_nsf": "411"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "d103900c07ac88d0c4253f96e233b088921b0731", "fields": {"formation": "Economie et activit\\u00e9s domestiques", "code_nsf": "422"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "8c7217c3b949f1ec25358082c937834c0fe691c8", "fields": {"formation": "Energie, g\\u00e9nie climatique (y compris \\u00e9nergie nucl\\u00e9aire, thermique, hydraulique ; utilit\\u00e9s : froid, climatisation, chauffage)", "code_nsf": "227"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "9df6cf0abed9169224891ba5895e78523a234a71", "fields": {"formation": "Accueil, h\\u00f4tellerie, tourisme", "code_nsf": "334"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "1bc370e66decc84aaa5271e6720c00467dae8862", "fields": {"formation": "D\\u00e9veloppement des capacit\\u00e9s d'orientation, d'insertion ou de r\\u00e9insertion sociales et professionnelles", "code_nsf": "415"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "a9664d51426b988539db0aebb52bc28e6ef3bd1e", "fields": {"formation": "Chimie", "code_nsf": "116"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "8c3cbd6ee2b8a21ec2f8b3b27404827ab8aedfd4", "fields": {"formation": "Travail du bois et de l'ameublement", "code_nsf": "234"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "01b23a8da5d4fb4098b808fff322595791348a27", "fields": {"formation": "Arts plastiques", "code_nsf": "132"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "aee958989ae0628f92ae913577e0b0ac999556bb", "fields": {"formation": "Journalisme, communication (y compris communication graphique et publicit\\u00e9)", "code_nsf": "321"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "b272211465878a9ab38a88f2bf402fc0c7b8481f", "fields": {"formation": "Documentation, biblioth\\u00e8ques, administration des donn\\u00e9es", "code_nsf": "325"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "462e37645ed3b59d10faa54226f5ffaf4236e327", "fields": {"formation": "Am\\u00e9nagement du territoire, d\\u00e9veloppement, urbanisme", "code_nsf": "341"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "e6482a67f00da225a32ae26e0a0feceb36e5c4d6", "fields": {"formation": "Sp\\u00e9cialit\\u00e9s militaires", "code_nsf": "346"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "ad9bd7761553b70c54bbc7afbab72f50081c06aa", "fields": {"formation": "Sciences de la vie", "code_nsf": "118"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "92de32733cd56ffd713707eab9657895c9c0a955", "fields": {"formation": "Economie", "code_nsf": "122"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "e7c27229763d1e8606342032371bf7e58dd6e2ba", "fields": {"formation": "Vie familiale, vie sociale et autres formations au d\\u00e9veloppement personnel", "code_nsf": "423"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "fa014b3a9b3f16ce54c08f441c65aa8951790254", "fields": {"formation": "Structures m\\u00e9talliques (y compris soudure, carrosserie, coque bateau, cellule avion)", "code_nsf": "254"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "9e09549aed80d5bb9938db645bf04a9038afd002", "fields": {"formation": "Sp\\u00e9cialit\\u00e9s concernant plusieurs capacit\\u00e9s", "code_nsf": "410"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "b2699e52f53d3cd51704f0edeeb71b9aa2830bf9", "fields": {"formation": "G\\u00e9ographie", "code_nsf": "121"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "cc17569715680d14d065503f17db600ec04c82c0", "fields": {"formation": "Ressources humaines, gestion du personnel, gestion de l'emploi", "code_nsf": "315"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "fff3776bbd85032f7c57c71570fdf09e805f7370", "fields": {"formation": "Physique-chimie", "code_nsf": "111"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "a6eef904573ad3206edb4684ad4556fffce7aeb2", "fields": {"formation": "Agro-alimentaire, alimentation, cuisine", "code_nsf": "221"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "d2a10ba5de68b5a6ce15de6641bd1c490b797463", "fields": {"formation": "Philosophie, \\u00e9thique et th\\u00e9ologie", "code_nsf": "127"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "596486810f8af6f07b38b6ff236f58b93fce1218", "fields": {"formation": "Sp\\u00e9cialit\\u00e9s plurivalentes de l'agronomie et de l'agriculture", "code_nsf": "210"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "5dc2d8a0a92bab18a6cb6f969bcba1c66aadf1ff", "fields": {"formation": "M\\u00e9canique a\\u00e9ronautique et spatiale", "code_nsf": "253"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "d76280ada83e00fee85196ea333870c65a4daceb", "fields": {"formation": "Nettoyage, assainissement, protection de l'environnement", "code_nsf": "343"}, "record_timestamp": "2017-03-22T23:05:05+01:00"},{"datasetid": "codes-nsf", "recordid": "6ed90c1186d2537198f80f220c252b4e04b3dae8", "fields": {"formation": "S\\u00e9curit\\u00e9 des biens et des personnes, police, surveillance (y compris hygi\\u00e8ne et s\\u00e9curit\\u00e9)", "code_nsf": "344"}, "record_timestamp": "2017-03-22T23:05:05+01:00"}]"""


def populate_cae_situations_and_career_stages(session):
    """
    Populate the database with default CAE situation options and career stages
    """
    # Populate CAE situations
    from caerp.models.user.userdatas import CaeSituationOption

    query = session.query(CaeSituationOption)
    if query.count() == 0:
        situation_cand = CaeSituationOption(label="Candidat", order=0)
        situation_conv = CaeSituationOption(
            label="En convention", is_integration=True, order=1
        )
        situation_es = CaeSituationOption(
            label="Entrepreneur salarié", is_integration=True, order=2
        )
        situation_out = CaeSituationOption(label="Sortie", order=3)
        session.add(situation_cand)
        session.add(situation_conv)
        session.add(situation_es)
        session.add(situation_out)
        session.flush()
    # Populate Career Stages
    from caerp.models.career_stage import CareerStage

    if CareerStage.query().count() == 0:
        for active, name, cae_situation_id, stage_type in (
            (True, "Diagnostic", None, None),
            (True, "Contrat CAPE", situation_conv.id, "entry"),
            (True, "Contrat CESA", situation_es.id, "contract"),
            (True, "Avenant contrat", None, "amendment"),
            (True, "Sortie", situation_out.id, "exit"),
        ):
            session.add(
                CareerStage(
                    active=active,
                    name=name,
                    cae_situation_id=cae_situation_id,
                    stage_type=stage_type,
                )
            )
        session.flush()


def populate_training_bpf_specialities(session):
    def _nsf_specialities_label_iterator(json_blob):
        rows = json.loads(json_blob)
        for row in rows:
            yield "{code_nsf} - {formation}".format(**row["fields"])

    from caerp.models.training.bpf import NSFTrainingSpecialityOption

    if NSFTrainingSpecialityOption.query().count() == 0:
        for label in _nsf_specialities_label_iterator(NSF_CODES):
            session.add(NSFTrainingSpecialityOption(label=label))
        session.flush()


def populate_access_rights(session):
    from caerp.models.user.access_right import AccessRight
    from caerp.consts.access_rights import ACCESS_RIGHTS

    for access_right in ACCESS_RIGHTS.values():
        name = access_right["name"]
        if session.query(AccessRight.id).filter(AccessRight.name == name).count() == 0:
            session.add(AccessRight(name=name))
    session.flush()


def populate_groups(session):
    """
    Populate the groups in the database
    """
    from sqlalchemy import select
    from caerp.consts.users import PREDEFINED_GROUPS
    from caerp.models.user.group import Group
    from caerp.models.user.access_right import AccessRight

    for group_dict in PREDEFINED_GROUPS:
        group = (
            session.execute(select(Group).where(Group.name == group_dict["name"]))
            .scalars()
            .first()
        )
        create_group = group is None
        if create_group:
            group = Group(
                name=group_dict["name"],
                label=group_dict["label"],
                account_type=group_dict["account_type"],
                default_for_account_type=group_dict.get(
                    "default_for_account_type", False
                ),
            )
            session.add(group)
        if create_group or not group_dict["editable"]:
            access_rights = group_dict.get("access_rights", [])
            for access_right in access_rights:
                right = session.execute(
                    select(AccessRight).where(AccessRight.name == access_right["name"])
                ).scalar_one()
                if right not in group.access_rights:
                    group.access_rights.append(right)
    session.flush()


def populate_system_user(session):
    """
    Create a system user with id 0
    """
    from caerp.models.user import User, Login

    if User.get(0) is None:
        system_user = User()
        system_user.firstname = ""
        system_user.lastname = "[ Traitement automatique enDI ]"
        system_user.email = "no-email"
        system_user.special = 1
        session.add(system_user)
        session.flush()
        system_user.id = 0
        session.merge(system_user)

    if Login.get(0) is None:
        system_user_login = Login()
        system_user_login.login = "caerp"
        system_user_login.pwd_hash = ""
        system_user_login.active = 1
        system_user_login.user_id = 0

        session.add(system_user_login)
        session.flush()
        system_user_login.groups.append("admin")
        system_user_login.id = 0
        session.merge(system_user_login)


def populate_accounting_balance_sheet_types(session):
    """
    Populate the database with balance sheet measure type (bilan)
    """
    from caerp.models.config import Config
    from caerp.models.accounting.balance_sheet_measures import (
        ActiveBalanceSheetMeasureType,
        PassiveBalanceSheetMeasureType,
    )

    if session.query(ActiveBalanceSheetMeasureType.id).count() == 0:
        active_types = [
            ("2", "Immobilisations", False, None),
            ("3", "Stocks", False, None),
            ("41", "Clients", False, None),
            ("5", "Banque", False, None),
            ("active", "Total Actif", True, "categories"),
        ]

        for order, data in enumerate(active_types):
            (
                account_prefix,
                label,
                is_total,
                total_type,
            ) = data
            session.add(
                ActiveBalanceSheetMeasureType(
                    account_prefix=account_prefix,
                    label=label,
                    is_total=is_total,
                    order=order,
                    total_type=total_type,
                )
            )

    if session.query(PassiveBalanceSheetMeasureType.id).count() == 0:
        passive_types = [
            ("10,-106", "Capital social", False, None),
            ("106", "Réserve", False, None),
            ("11", "Report à nouveau", False, None),
            ("12", "Résultat", False, None),
            ("14,15", "Provisions", False, None),
            ("40,42", "Fournisseurs", False, None),
            ("43,44", "Dettes sociales et fiscales", False, None),
            ("16,17,18", "Dettes financières", False, None),
            ("passive", "Total Passif", True, "categories"),
        ]

        for order, data in enumerate(passive_types):
            (
                account_prefix,
                label,
                is_total,
                total_type,
            ) = data
            session.add(
                PassiveBalanceSheetMeasureType(
                    account_prefix=account_prefix,
                    label=label,
                    is_total=is_total,
                    order=order,
                    total_type=total_type,
                )
            )
        session.flush()


def populate_accounting_treasury_measure_types(session):
    """
    Populate the database with treasury measure types
    """
    from caerp.models.config import Config
    from caerp.models.accounting.treasury_measures import (
        TreasuryMeasureTypeCategory,
        TreasuryMeasureType,
    )

    if session.query(TreasuryMeasureTypeCategory.id).count() == 0:
        categories = []
        for order, name in enumerate(["Référence", "Future", "Autres"]):
            category = TreasuryMeasureTypeCategory(label=name, order=order)
            session.add(category)
            session.flush()
            categories.append(category.id)

        types = [
            (0, "5", "Trésorerie du jour", True, "account_prefix"),
            (
                0,
                "42,-421,-425,43,44",
                "Impôts, taxes et cotisations dues",
                False,
                None,
            ),
            (0, "40", "Fournisseurs à payer", False, None),
            (0, "Référence", "Trésorerie de référence", True, "categories"),
            (1, "421", "Salaires à payer", False, None),
            (1, "41", "Clients à encaisser", False, None),
            (1, "425", "Notes de dépenses à payer", False, None),
            (
                1,
                "{Référence}+{Future}",
                "Trésorerie future",
                True,
                "complex_total",
            ),
            (2, "1,2,3", "Comptes bilan non pris en compte", False, None),
            (
                2,
                "{Référence}+{Future}+{Autres}",
                "Résultat de l'enseigne",
                True,
                "complex_total",
            ),
        ]
        for order, data in enumerate(types):
            (
                category_index,
                account_prefix,
                label,
                is_total,
                total_type,
            ) = data
            category_id = categories[category_index]
            session.add(
                TreasuryMeasureType(
                    category_id=category_id,
                    account_prefix=account_prefix,
                    label=label,
                    is_total=is_total,
                    order=order,
                    total_type=total_type,
                )
            )
        if not Config.get_value("treasury_measure_ui"):
            Config.set("treasury_measure_ui", "Trésorerie du jour")
        session.flush()


def populate_accounting_income_statement_measure_types(session):
    """
    Populate the database with treasury measure types
    """
    from caerp.models.accounting.income_statement_measures import (
        IncomeStatementMeasureTypeCategory,
    )

    if session.query(IncomeStatementMeasureTypeCategory.id).count() == 0:
        for order, category in enumerate(
            ("Produits", "Achats", "Charges", "Salaires et Cotisations")
        ):
            session.add(IncomeStatementMeasureTypeCategory(label=category, order=order))
        session.flush()


def populate_bookentry_config(session):
    from caerp.models.config import Config

    initial_values = [
        (
            "bookentry_facturation_label_template",
            "{invoice.customer.label} {company.name}",
        ),
        (
            "bookentry_rg_interne_label_template",
            "RG COOP {invoice.customer.label} {company.name}",
        ),
        (
            "bookentry_rg_client_label_template",
            "RG {invoice.customer.label} {company.name}",
        ),
        (
            "internalbookentry_facturation_label_template",
            "Int {invoice.customer.label} {company.name}",
        ),
        (
            "bookentry_payment_label_template",
            "{company.name} / Rgt {invoice.customer.label}",
        ),
        (
            "internalbookentry_payment_label_template",
            "{company.name} / Rgt Int {invoice.customer.label}",
        ),
        (
            "bookentry_expense_label_template",
            "{beneficiaire}/frais {expense_date:%-m %Y}",
        ),
        (
            "bookentry_expense_payment_main_label_template",
            "{beneficiaire_LASTNAME} / REMB FRAIS {expense_date:%B/%Y}",
        ),
        (
            "bookentry_expense_payment_waiver_label_template",
            "Abandon de créance {beneficiaire_LASTNAME} {expense_date:%B/%Y}",
        ),
        (
            "bookentry_supplier_invoice_label_template",
            "{company.name} / Fact {supplier.label}",
        ),
        (
            "bookentry_supplier_payment_label_template",
            "{company.name} / Rgt {supplier.label}",
        ),
        (
            "bookentry_supplier_invoice_user_payment_label_template",
            "{beneficiaire_LASTNAME} / REMB FACT {supplier_invoice.official_number}",
        ),
        (
            "bookentry_supplier_invoice_user_payment_waiver_label_template",
            "Abandon de créance {beneficiaire_LASTNAME}"
            " {supplier_invoice.official_number}",
        ),
        (
            "internalbookentry_supplier_invoice_label_template",
            "{company.name} / Fact Int {supplier.label}",
        ),
        (
            "internalbookentry_supplier_payment_label_template",
            "{company.name} / Rgt Int {supplier.label}",
        ),
        ("ungroup_supplier_invoices_export", "0"),
        ("receipts_grouping_strategy", ""),
    ]
    for key, val in initial_values:
        if not Config.get_value(key):
            Config.set(key, val)


def populate_project_types(session):
    from caerp.models.project.types import (
        ProjectType,
        BusinessType,
    )

    for (
        name,
        label,
        subtype_label,
        private,
        default,
        include_price_study,
        active,
        tva_on_margin,
        with_business,
        ht_compute_mode_allowed,
        ttc_compute_mode_allowed,
    ) in (
        (
            "default",
            "Dossier classique",
            "Affaire simple",
            False,
            True,
            False,
            True,
            False,
            False,
            True,
            True,
        ),
        (
            "training",
            "Convention de formation",
            "Formation",
            True,
            False,
            False,
            True,
            False,
            True,
            True,
            False,
        ),
        (
            "construction",
            "Chantier",
            "Chantier",
            True,
            False,
            True,
            True,
            False,
            True,
            True,
            False,
        ),
        (
            "travel",
            "Dossier voyage",
            "Voyage",
            False,
            False,
            False,
            False,
            True,
            True,
            False,
            True,
        ),
    ):
        ptype = ProjectType.query().filter_by(name=name).first()
        if ptype is None:
            ptype = ProjectType(
                name=name,
                label=label,
                editable=False,
                private=private,
                default=default,
                include_price_study=include_price_study,
                active=active,
                with_business=with_business,
            )
            session.add(ptype)
            session.flush()
            if name != "default":
                default_btype = BusinessType.query().filter_by(name="default").first()
                default_btype.other_project_types.append(ptype)
                session.merge(default_btype)
                session.flush()

        if session.query(BusinessType.id).filter_by(name=name).count() == 0:
            session.add(
                BusinessType(
                    name=name,
                    label=subtype_label,
                    editable=False,
                    private=private,
                    project_type_id=ptype.id,
                    tva_on_margin=tva_on_margin,
                )
            )
    session.flush()


def populate_contract_types(session):
    """
    Populate the database with default contract types
    """
    from caerp.models.career_path import TypeContratOption

    query = session.query(TypeContratOption)
    if query.filter(TypeContratOption.label == "CDD").count() == 0:
        session.add(TypeContratOption(label="CDD", order=0))
    if query.filter(TypeContratOption.label == "CDI").count() == 0:
        session.add(TypeContratOption(label="CDI", order=0))
    if query.filter(TypeContratOption.label == "CESA").count() == 0:
        session.add(TypeContratOption(label="CESA", order=0))
    session.flush()


def _add_filetype_and_reqs(session, business_type_label, filetype, requirements):
    """ """
    from caerp.models.files import FileType
    from caerp.models.project.types import BusinessType
    from caerp.models.project.file_types import BusinessTypeFileType

    if session.query(FileType.id).filter_by(label=filetype).count() == 0:
        f = FileType(label=filetype)
        session.add(f)
        session.flush()
        btype_id = (
            session.query(BusinessType.id).filter_by(name=business_type_label).scalar()
        )

        for req_dict in requirements:
            req = BusinessTypeFileType(
                file_type_id=f.id,
                business_type_id=btype_id,
                doctype=req_dict["doctype"],
                requirement_type=req_dict["req_type"],
                validation=req_dict.get("validation", False),
            )
            session.add(req)
        session.flush()


def populate_file_types_and_requirements(session):
    """
    Add default file types to the database
    """
    filetype = "Formation : Convention"
    requirements = [
        {
            "doctype": "business",
            "req_type": "project_mandatory",
            "validation": True,
        },
        {
            "doctype": "invoice",
            "req_type": "project_mandatory",
        },
    ]
    _add_filetype_and_reqs(session, "training", filetype, requirements)
    filetype = "Formation : Émargement"
    requirements = [
        {
            "doctype": "business",
            "req_type": "business_mandatory",
            "validation": True,
        },
        {
            "doctype": "invoice",
            "req_type": "business_mandatory",
        },
    ]
    _add_filetype_and_reqs(session, "training", filetype, requirements)
    filetype = "Document fournisseur : Facture"
    requirements = []
    _add_filetype_and_reqs(session, "supplier_order", filetype, requirements)
    filetype = "Document fournisseur : Devis"
    requirements = []
    _add_filetype_and_reqs(session, "supplier_order", filetype, requirements)


def populate_number_templates(session):
    from caerp.models.config import Config

    defaults = {
        "internalinvoice_number_template": "INT-{SEQGLOBAL}",
        "invoice_number_template": "{SEQGLOBAL}",
        "expensesheet_number_template": "{SEQGLOBAL}",
        "supplierinvoice_number_template": "{SEQGLOBAL}",
        "internalsupplierinvoice_number_template": "INT-{SEQGLOBAL}",
        "sale_pdf_filename_template": "{type_document}_{numero}",
    }
    for key, value in defaults.items():
        if not Config.get_value(key):
            Config.set(key, value)
    session.flush()


def populate_banks(session):
    """
    Populate the banks in the database
    """
    from caerp.models.payments import Bank

    if session.query(Bank.id).count() == 0:
        for order, bank_name in enumerate(
            (
                "Allianz Banque",
                "Axa Banque",
                "Banque Courtois",
                "Banque de France",
                "Banque Delubac",
                "Banque Populaire",
                "BARCLAYS",
                "BFM",
                "BNP",
                "Boursorama Banque",
                "BPCE",
                "BTP Banque",
                "Caisse d'Epargne",
                "CIC",
                "Crédit Agricole",
                "Crédit Coopératif",
                "Crédit du Nord",
                "Crédit Mutuel",
                "HSBC",
                "ING Direct",
                "La Banque Postale",
                "La NEF",
                "LCL",
                "Société Générale",
                "Société Marseillaise de Crédit",
            )
        ):
            session.add(Bank(label=bank_name, order=order))
        session.flush()


def populate_expense_types(session):
    from caerp.models.expense.types import ExpenseType

    if session.query(ExpenseType.id).filter_by(internal=True).count() == 0:
        session.add(
            ExpenseType(
                internal=True,
                contribution=False,
                label="Prestation interne",
                code="604020",
            )
        )
        session.flush()


def populate_main_config(session):
    """
    Setup main configuration options
    """
    from caerp.models.config import Config

    config_options = (
        ("estimation_validity_duration_default", "3 mois"),
        ("task_display_units_default", "1"),
        ("task_display_ttc_default", "0"),
        ("estimation_payment_display_default", "NONE"),
    )
    for key, value in config_options:
        if session.query(Config).filter(Config.name == key).count() == 0:
            Config.set(key, value)
    session.flush()


def populate_task_mentions(session):
    """
    Populate task mentions
    Les autres mentions sont issues d'une migration précédente
    """
    from caerp.models.task.mentions import TaskMention

    query = session.query(TaskMention.id)
    query = query.filter_by(title="Informations spéciales agence de voyage")
    if query.count() == 0:
        for title, full_text, help_text in (
            (
                "Informations spéciales agence de voyage",
                "Régime particulier – Agences de voyage : TVA calculée sur"
                " marge                 selon l'article 266.-1 du CGI",
                "Mentions spéciales agence de voyage",
            ),
        ):
            session.add(
                TaskMention(
                    label=title,
                    title=title,
                    full_text=full_text,
                    help_text=help_text,
                    active=False,
                )
            )
    session.flush()


def populate_business_type_task_mention(session):
    """
    Populate travel type task mentions default values
    """
    from caerp.models.task.mentions import TaskMention
    from caerp.models.project.mentions import BusinessTypeTaskMention
    from caerp.models.project.types import BusinessType

    query = session.query(BusinessType.id).filter_by(label="Voyage")
    travel_type_id = query.scalar()
    query = session.query(TaskMention.id)
    query = query.filter_by(title="Informations spéciales agence de voyage")
    travel_mentions_id = query.scalar()
    if travel_mentions_id is not None and travel_type_id is not None:
        query = session.query(BusinessTypeTaskMention.task_mention_id)
        query = query.filter_by(task_mention_id=travel_mentions_id)
        if query.count() == 0:
            for index, doctype in enumerate(
                (
                    "estimation",
                    "invoice",
                    "cancelinvoice",
                )
            ):
                session.add(
                    BusinessTypeTaskMention(
                        task_mention_id=travel_mentions_id,
                        business_type_id=travel_type_id,
                        doctype=doctype,
                        mandatory=True,
                    )
                )
    session.flush()


def populate_doctype_label_override(session):
    """Populate doctype label overrides

    Only if there is none yet.
    """
    from caerp.models.project.naming import LabelOverride
    from caerp.models.project.types import BusinessType

    query = session.query(LabelOverride)

    default_overrides = [
        ("construction", "signed_agreement", "Bon pour travaux"),
    ]

    if query.count() == 0:
        for business_type_name, label_key, label_value in default_overrides:
            obj = LabelOverride(
                business_type=BusinessType.get_by_name(business_type_name),
                label_key=label_key,
                label_value=label_value,
            )
            session.add(obj)
        session.flush()


def populate_tva_and_products(session):
    from caerp.models.tva import Tva, Product

    if session.query(Product).filter_by(internal=True).count() == 0:
        min_value = (
            session.query(sqlalchemy.func.min(Tva.value))
            .filter(Tva.value <= 0)
            .scalar()
        )

        if min_value is not None:
            value = min_value - 100
        else:
            value = 0

        tva = Tva(value=value, name="Exonération")
        session.add(tva)
        session.flush()
        product1 = Product(name="Prestation interne", tva=tva, internal=True)
        session.add(product1)
        session.flush()


def populate_accounting_book_modules(session):
    """
    Crée les Modules d'écritures pour les contribution et assurance
    """
    from caerp.models.accounting.bookeeping import CustomInvoiceBookEntryModule

    for doctype, prefix in (("invoice", ""), ("internalinvoice", "Int ")):
        for title, name, template in (
            (
                "Module de contribution",
                "contribution",
                "{invoice.customer.label} {company.name}",
            ),
            ("Assurance", "insurance", "Assurance {company.name}"),
        ):
            module = (
                CustomInvoiceBookEntryModule.query()
                .filter_by(name=name, doctype=doctype)
                .first()
            )
            if not module:
                module = CustomInvoiceBookEntryModule(
                    name=name,
                    title=title,
                    label_template="%s%s" % (prefix, template),
                    percentage=0,
                    enabled=False,
                    custom=False,
                    doctype=doctype,
                    compte_cg_credit="",
                    compte_cg_debit="",
                )
                session.add(module)
                session.flush()


def populate_form_field_definitions(session):
    """
    Crée les définitions pour les champs personnalisables des formulaires
    """
    from caerp.models.form_options import FormFieldDefinition

    for field in (
        {
            "field_name": "workplace",
            "title": "Lieu d'exécution",
            "required": False,
            "visible": False,
        },
        {
            "field_name": "validity_duration",
            "title": "Durée de validité du devis",
            "required": True,
        },
        {
            "field_name": "first_visit",
            "title": "Date de première visite",
            "visible": False,
        },
        {
            "field_name": "start_date",
            "title": "Date de début de prestation",
            "visible": False,
        },
        {
            "field_name": "end_date",
            "title": "Date de fin de prestation",
            "visible": False,
        },
        {
            "field_name": "insurance_id",
            "title": "Assurance Professionnelle",
            "visible": False,
        },
    ):
        if (
            FormFieldDefinition.query()
            .filter_by(field_name=field["field_name"])
            .count()
            == 0
        ):
            field_def = FormFieldDefinition(form="task", **field)
            session.add(field_def)
            session.flush()


def populate_price_study_config(session):
    from caerp.models.config import Config

    for key in ("price_study_uses_contribution", "price_study_uses_insurance"):
        if Config.get_value(key, default="toto") == "toto":
            Config.set(key, True)
        session.flush()


def populate_notification_types_and_channels(session):
    from caerp.models.notification import NotificationEventType, NotificationChannel

    for key, label, channel, status_type in (
        ("task:status:valid", "Devis/Facture Validé", "email", "valid"),
        ("task:status:invalid", "Devis/facture invalidé", "email", "invalid"),
        ("task:status:paid", "Facture encaissée", "email", "valid"),
        ("task:status:resulted", "Facture encaissée entièrement", "email", "valid"),
        ("expense:status:valid", "Notes de dépenses validées", "email", "valid"),
        ("expense:status:invalid", "Notes de dépenses invalidées", "email", "invalid"),
        ("expense:status:paid", "Notes de dépenses payées", "email", "valid"),
        (
            "expense:status:resulted",
            "Notes de dépenses payées entièrement",
            "email",
            "valid",
        ),
        ("supplier_invoice:status:valid", "", "email", "valid"),
        ("supplier_invoice:status:invalid", "", "email", "invalid"),
        ("supplier_invoice:status:paid", "", "email", "valid"),
        ("supplier_invoice:status:resulted", "", "email", "valid"),
        ("supplier_order:status:valid", "", "email", "valid"),
        ("supplier_order:status:invalid", "", "email", "invalid"),
        ("supplier_order:status:paid", "", "email", "valid"),
        ("supplier_order:status:resulted", "", "email", "valid"),
        ("message:internal", "Message interne", "message", "neutral"),
        ("message:system", "Message d'alerte système", "alert", "caution"),
        ("userdata:reminder", "Rappel de gestion sociale", "message", "document"),
        ("workshop:reminder", "Rappel atelier", "message", "calendar"),
        ("activity:reminder", "Rappel de rendez-vous", "message", "calendar"),
    ):
        if NotificationEventType.get_type(key) is None:
            session.add(
                NotificationEventType(
                    key=key,
                    label=label,
                    default_channel_name=channel,
                    status_type=status_type,
                )
            )
            session.flush()

    for name, label in (
        ("email", "Par e-mail"),
        ("message", "Notification interne (sous la cloche)"),
        ("alert", "Modale à la connexion"),
        ("header_message", "Au dessus du header sur toutes les pages"),
    ):
        if NotificationChannel.get_by_name(name) is None:
            session.add(NotificationChannel(name=name, label=label))
            session.flush()


def populate_thirdparty_account_mandatory(session):
    """
    Setup config thirdparty_account_mandatory options
    """
    from caerp.models.config import Config

    config_options = (
        ("thirdparty_account_mandatory_user", "1"),
        ("thirdparty_account_mandatory_customer", "0"),
        ("thirdparty_account_mandatory_supplier", "0"),
    )
    for key, value in config_options:
        if session.query(Config).filter(Config.name == key).count() == 0:
            Config.set(key, value)
    session.flush()


def populate_sale_catalog_sale_product_taskline_templates(session):
    """
    Setup the initial templates to generate tasklines from training-related products

    """
    from caerp.models.config import Config

    default_vals = (
        (
            "sale_catalog_sale_product_training_taskline_template",
            """<p>&nbsp;</p>
<p><strong>Objectifs de la Formation :</strong></p>
<p>{goals}</p>
<p><strong>Dur&eacute;e :</strong> {duration_days} jours - {duration_hours} heures</p>
<p><strong>Formateur&middot;ice :</strong> {trainer} </p>
<p><strong>Modalit&eacute; :</strong> {presence_modality_label} - {group_size_label} - {mixing_modality_label} - {accessibility}</p>
<p><strong>Public :</strong> {for_who}</p>
<p><strong>Pr&eacute;requis :</strong></p>
<p>{prerequisites}</p>
<p><strong>M&eacute;thodes p&eacute;dagogiques :</strong></p>
<p>{teaching_method}</p>
<p><strong>Modalit&eacute;s d'&eacute;valuation :</strong></p>
<p>{evaluation}</p>
<p><strong>D&eacute;lai d'&eacute;ligibilit&eacute; : </strong>{access_delay}</p>
<p><strong>Lieu d'intervention :&nbsp; </strong>XXXXXXXXXXXXX</p>
<p><strong>Dates d'intervention : </strong>XXXXXXXXXXXXX</p>
<p><strong>Certification :</strong>{certification_name} {rncp_rs_code} (certifi&eacute; le&nbsp; {certification_date} par {certificator_name})</p>
<p><strong>Passerelles : </strong>{gateways}</p>""",
        ),
        (
            "sale_catalog_sale_product_vae_taskline_template",
            """<p>&nbsp;</p>
<p><strong>Objectifs de la VAE :</strong></p>
<p>{goals}</p>
<p><strong>Dur&eacute;e :</strong> {duration_days} jours - {duration_hours} heures</p>
<p><strong>Formateur&middot;ice :</strong> {trainer} </p>
<p><strong>Modalit&eacute; :</strong> {presence_modality_label} - {group_size_label} - {accessibility}</p>
<p><strong>Lieu d'intervention :&nbsp; </strong>XXXXXXXXXXXXX</p>
<p><strong>Dates d'intervention : </strong>XXXXXXXXXXXXX</p>
<p><strong>Public :</strong> {for_who}</p>
<p><strong>Contenu :</strong></p>
<p>{content}</p>
<p><strong>M&eacute;thodes p&eacute;dagogiques :</strong></p>
<p>{teaching_method}</p>
<p><strong>Modalit&eacute;s d'&eacute;valuation :</strong></p>
<p>{evaluation}</p>
<p><strong>Processus d'&eacute;ligibilit&eacute; :</strong></p>
<p>{eligibility_process}</p>
<p><strong>D&eacute;lai d'&eacute;ligibilit&eacute; : </strong>{access_delay}</p>""",
        ),
    )
    for key, val in default_vals:
        if not Config.get(key):
            Config.set(key, val)
    session.flush()


class PopulateRegistry:
    BASE_FUNCTIONS = [
        populate_cae_situations_and_career_stages,
        populate_access_rights,
        populate_groups,
        populate_system_user,
        populate_accounting_treasury_measure_types,
        populate_accounting_income_statement_measure_types,
        populate_accounting_balance_sheet_types,
        populate_bookentry_config,
        populate_project_types,
        populate_contract_types,
        populate_file_types_and_requirements,
        populate_number_templates,
        populate_training_bpf_specialities,
        populate_banks,
        populate_expense_types,
        populate_main_config,
        populate_task_mentions,
        populate_business_type_task_mention,
        populate_doctype_label_override,
        populate_tva_and_products,
        populate_accounting_book_modules,
        populate_form_field_definitions,
        populate_price_study_config,
        populate_notification_types_and_channels,
        populate_thirdparty_account_mandatory,
        populate_sale_catalog_sale_product_taskline_templates,
    ]

    EXTRA_FUNCTIONS = []

    @classmethod
    def add_function(
        cls, populate_function: Callable[[sqlalchemy.orm.Session], None]
    ) -> None:
        """
        Plug-in a populate function.

        this function may be used by plugins to plug their functions in.

        The new function will be called last on populate_database invocation.
        """
        cls.EXTRA_FUNCTIONS.append(populate_function)

    @classmethod
    def get_functions(cls):
        return cls.BASE_FUNCTIONS + cls.EXTRA_FUNCTIONS


def populate_database():
    """
    Populate the database with default values
    """
    logger.debug("Populating the database")
    session = DBSESSION()
    for func in PopulateRegistry.get_functions():
        begin()
        session = DBSESSION()
        try:
            func(session)
        except sqlalchemy.exc.OperationalError as e:
            print("There is an error in the population process :")
            print(e)
        commit()
