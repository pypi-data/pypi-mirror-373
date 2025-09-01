let trays = {};

Tray = function (tray_id, max_items=10) {
    self = this;
    trays[tray_id] = self;

    const tray = $(tray_id);
    const tray_header = tray.find('.js-tray_header');
    const tray_body = tray.find('.js-tray_body');
    const tray_body_col = tray.find('.js-tray_body_col');
    const tray_footer = tray.find('.js-tray_footer');
    const tray_header_title = tray.find('.js-tray_header_title');
    const resources = tray.find('.js-tray_resources');

    this.closeTray = function () {
        tray.addClass('hidden-tray');
    };

    this.openTray = function (flush_body=false) {
        tray.removeClass('hidden-tray');
        if (flush_body) {
            tray_body_col.empty();
        }
    };

    this.updateHeaderTitle = function (title) {
        tray_header_title.html(title);
    };

    this.addOrUpdateProgressBarItem = function (item_id, title, progress_value) {
        const exist_items = $(`#${item_id}`);

        if (!exist_items.length) {
            const progress_bar_item = resources.find('.js-tray_progress_bar_item').clone();
            progress_bar_item.attr('id', item_id);
            progress_bar_item.find('.js-title').html(title);
            tray_body_col.append(progress_bar_item);
        }
        self.updateItemProgressBar(item_id, progress_value);
        self.addProgressBarItemBarColor(item_id, '#28B779')
    };

    this.addProgressBarItemBarColor = function (item_id, color) {
        const bar = $(`#${item_id}`).find('.js-bar');
        bar.css({'background-color': color});
    };

    this.addInfoRow = function(item_id, info) {
        const exist_items = $(`#${item_id}`);

        if (exist_items.length) {
            const tray_item_row = resources.find('.js-tray_item_row').clone();
            tray_item_row.html(info);
            exist_items.append(tray_item_row);
        }
    };

    this.updateItemProgressBar = function (item_id, progress_value) {
        const item = tray_body_col.find(`#${item_id}`);
        const bar = item.find('.js-bar');
        if (progress_value <= 100) {
            bar.css({'width': `${progress_value}%`});
        }
    };

    this.removeItem = function (item_id) {
        tray_body_col.find(`#${item_id}`).remove();
    };

    this.controlItemsCount = function () {
        const items = tray_body_col.find('.js-tray_item');
        if (items.length > max_items) {
            items.last().remove();
        }
    };

    this.initSignals = function () {
        tray.on('click', '.js-tray_close', function (event) {
            self.closeTray();
            event.preventDefault();
        });
    };
};