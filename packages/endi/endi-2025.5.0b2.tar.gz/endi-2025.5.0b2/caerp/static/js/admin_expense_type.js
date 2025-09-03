/** Show child element only if parent field (type=checkbox) is checked
*/
class TVAOnMarginFieldsLink {
    constructor(parentEl, childEl) {
        this.parentEl = parentEl;
        this.childEl = childEl;
        this.update();
        this.install();
    }
    install() {
        let self = this;
        this.parentEl.change(function() {
            self.update()
        });
    }
    update() {
        if (this.parentEl.is(':checked')) {
            this.childEl.show();
        } else {
            this.childEl.hide();
        }
    }
}

$(function() {
    new TVAOnMarginFieldsLink(
        $('input[name=tva_on_margin]'),
        $('.form-group.item-compte_produit_tva_on_margin'),
    );
});
