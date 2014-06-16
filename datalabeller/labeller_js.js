//%%javascript
require(["widgets/js/widget"], function(WidgetManager){
    
    var LabellerView = IPython.DOMWidgetView.extend( {
        render: function(){
            
            this.$canvas = $('<canvas />')
                .attr('width', '100%')
                .attr('height', '10')
                .attr('style', 'background: blue;')
                .attr('tabindex', '1')
                .appendTo(this.$el);
        },
        
        events: {
            'keydown': 'keypress',
            'click': 'click',
        },

        keypress: function(e) {
            var code = e.keyCode || e.which;
            this.send({event: 'keypress', code: code});
        },

        click: function(e) {
            this.send({event: 'click', button: e.button});
        }
    });
    
    WidgetManager.register_widget_view('LabellerView', LabellerView);
});
