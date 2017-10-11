define([
    'jquery',
    'underscore',
    'module',
    'views/shared/controls/Control',
    'views/shared/controls/colors/ColorRangeLabelControl',
    'splunk_monitoring_console/views/settings/overview_preferences/components/ColorRangeFromLabelControl',
    'views/shared/controls/colors/ColorRangeInputControl',
    'views/shared/controls/colors/ColorRangeColorControl',
    'splunk_monitoring_console/views/settings/overview_preferences/components/GradientColorRangeColorControl',
    'models/Base',
    'views/shared/controls/colors/ColorRangeControlRow'
], function(
    $,
    _,
    module,
    Control,
    LabelControl,
    FromLabelControl,
    InputControl,
    ColorControl,
    GradientColorControl,
    BaseModel,
    ColorRangeControlRow
    ) {

    return ColorRangeControlRow.extend({
        moduleId: module.id,
        initialize: function() {
            Control.prototype.initialize.apply(this, arguments);
            this.model.to = this.model;
            this.model.from = this.options.fromModel;
            this.displayMinMaxLabels = this.options.displayMinMaxLabels;
            this.rangesGradient = this.options.rangesGradient;
            this.initRowComponents();
        },

        initRowComponents: function() {
            var i = this.collection.indexOf(this.model.to);
            if (this.model.to.get('value') === 'more') {
                this.createFromLabelControl(this.model.from, 'maxFrom');
                // Set row's right control to label 'max'
                this.createLabelControl(this.model.to, 'max', 'or', 'color-control-right-col');
                this.createColorControl(this.model.to, 'max');
            } else {
                if (i === 1) {
                    // Left control should be an input instead of a label
                    if (isNaN(this.model.to.get('value'))) {
                        this.createLabelControl(this.model.to, this.model.to.cid, '', 'color-control-full-col');
                    } else {
                        this.createInputControl(this.model.from, this.model.from.cid, 'from', 'color-control-left-col');
                        this.createInputControl(this.model.to, this.model.to.cid, 'to');
                    }
                    
                } else {
                    // Most range values get both label and input controls.
                    // Use previous range value to power label.
                    if (isNaN(this.model.to.get('value'))) {
                        this.createLabelControl(this.model.to, this.model.to.cid, '', 'color-control-full-col');
                    } else {
                        this.createFromLabelControl(this.model.from, this.model.from.cid);
                        this.createInputControl(this.model.to, this.model.to.cid, 'to', '');
                    }
                }
                this.createColorControl(this.model.to, this.model.to.cid);
            }
        },

        createLabelControl: function(model, id, label, customClass) {
            var value = this.model.get('value');
            this.children['labelView_' + id] = new LabelControl({
                model: model,
                label: _(label).t(),
                value: value === 'more' ? _('more').t() : value,
                customClass: customClass
            });
        },

        createFromLabelControl: function(model, id, customClass) {
            this.children['labelView_' + id] = new FromLabelControl({
                model: model,
                label: _('from').t(),
                customClass: customClass
            });
        },

        createColorControl: function(model, id) {
            if (model.get('color') && model.get('color').length > 0) {
                if(this.rangesGradient) {
                    this.children['colorView_' + id] = new GradientColorControl({
                        model: model,
                        paletteColors: this.options.paletteColors,
                        rangeColors: this.options.rangeColors
                    });
                } else {
                    this.children['colorView_' + id] = new ColorControl({
                        model: model,
                        paletteColors: this.options.paletteColors
                    });
                }
            }
        }

    });

});