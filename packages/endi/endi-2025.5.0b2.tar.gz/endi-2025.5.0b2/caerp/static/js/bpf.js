/** Show subcontract details only if there are subcontracts and parent field is visible
 */
class SubContractFields {
    constructor(parentSelector, childSelectors) {
        this.parentSelector = parentSelector;
        this.childSelectors = childSelectors;
        this.update();
        this.install();
    }
    install() {
        let self = this;
        $(this.parentSelector).change(function() {
            self.update();
        });
    }
    update() {
        let parentVal = $(this.parentSelector).val();
        for (let i of this.childSelectors) {
            let formGroup = $(i).parent('.form-group');
            if (parentVal === 'no' || $(this.parentSelector).is(':hidden')) {
                $(i).val(0);
                formGroup.hide();
            } else {
                formGroup.show();
            }
        }
    }
}

/** When a training is totally subcontracted, help filling
 *
 * - auto-fill subcontracted hours/trainees
 * - hide those auto-filled fields.
 */
class SubContractTotalsLink {
    constructor(parentSelector, linkedFieldsSelectors) {
        this.parentSelector = parentSelector;
        this.linkedFieldsSelectors = linkedFieldsSelectors;
        this.update();
        this.install();
    }
    install() {
        let self = this;
        $(this.parentSelector).change(function() {
            self.update();
        });
        for (let i of this.linkedFieldsSelectors) {
            $(i.src).change(function() {
                self.update();
            });
        }
    }
    update() {
        let parentVal = $(this.parentSelector).val();
        for (let i of this.linkedFieldsSelectors) {
            let srcEl = $(i.src);
            let targetEl = $(i.target);

            if (parentVal === 'full') {
                targetEl.val(srcEl.val());
                targetEl.parent('.form-group').hide();
            } else if (parentVal === 'part') {
                targetEl.parent('.form-group').show();
            }
        }
    }
}

/** Show trainee & hours count only if several trainee types
 */
class TraineeTypeFields {
    constructor(parentSelector, childSelectors) {
        this.parentSelector = parentSelector;
        this.childSelectors = childSelectors;
        this.update();
        this.install();
    }
    install() {
        let self = this;
        let deformSeq = $(this.parentSelector).parentsUntil('.deform-seq');
        console.log(deformSeq);
        let seqAddButton = deformSeq.find('.deform-seq-add');
        seqAddButton.click(function() {self.update()});
    }
    update() {
        let parentOccurences = $(this.parentSelector+':visible').length;
        for (let i of this.childSelectors) {
            let formGroup = $(i).parentsUntil('.deform-seq-item','.form-group');
            if (parentOccurences == 1) {
                formGroup.hide();
                $(i).val(0); // backend will fill it appropriately
            } else {
                formGroup.show();
            }
        }
    }
}

/** In case we are a subcontract, hide some fields
 *
 * BPF 10443*17 : Les données relatives aux actions confiées à votre organisme
 * par un autre organisme de formation ne sont pas à comptabiliser dans les cadres
 * F ; elles doivent figurer dans le cadre G qui recense les données relatives
 * aux actions pour lesquelles vous êtes intervenus en sous-traitance et elles
 * correspondent aux produits indiqués ligne 10 du cadre C.
 *
 * Only show/hide is handled here, value enforcement is handled in backend.
 */
class SubcontractSimplification {
    constructor(parentSelector, childSelectors, linkedControllers) {
        this.parentSelector = parentSelector;
        this.childSelectors = childSelectors;
        this.linkedControllers = linkedControllers;
        this.update();
        this.install();
    }

    install() {
        $(this.parentSelector).change(this.update.bind(this))
    }

    update() {
        const isSubcontract = $(this.parentSelector).val() === 'true'
        const action = isSubcontract ?
            x => x.hide()
          : x => x.show()
        for (let childSelector of this.childSelectors) {
            action($(childSelector))
        }
        for (const controller of this.linkedControllers) {
            controller.update()
        }
    }
}
