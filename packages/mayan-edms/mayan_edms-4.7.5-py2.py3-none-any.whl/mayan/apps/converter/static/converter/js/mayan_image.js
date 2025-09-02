'use strict';

class MayanImage {
    constructor (options) {
        this.element = options.element;
    }

    static async setup (options) {
        this.options = options || {};

        $().fancybox({
            afterShow: function (instance, current) {
                $('a.a-caption').on('click', function(event) {
                    instance.close(true);
                });
            },
            animationEffect: 'fade',
            animationDuration : 100,
            buttons : [
                'fullScreen',
                'close'
            ],
            idleTime: false,
            infobar: true,
            selector: 'a.fancybox',
        });
    }

    static async initialize () {
        const eventHandlerImageError = function (event) {
            const $this = $(this);

            $this.siblings('.lazyload-spinner-container').remove();
            $this.removeClass('pull-left');

            $.ajax({
                async: true,
                dataType: 'json',
                error: function(jqXHR, textStatus, errorThrown) {
                    $this.off('error', eventHandlerImageError);

                    if (jqXHR.hasOwnProperty('responseJSON')) {
                        if (jqXHR.responseJSON.hasOwnProperty('app_image_error_image_template')) {
                            const $container = $this.parent().parent().parent();
                            const template = jqXHR.responseJSON['app_image_error_image_template']
                            $container.html(template);
                        }
                    }
                },
                // Need to set mimeType only when run from local file.
                mimeType: 'text/html; charset=utf-8',
                type: 'GET',
                url: $this.attr('src'),
            });
        }

        const observer = new IntersectionObserver(function(items) {
            items.forEach((item) => {
                if (item.isIntersecting) {
                    const $this = $(item.target);
                    const dataSrc = $this.attr('data-src');

                    $this.attr('src', dataSrc);
                    $this.on('error', eventHandlerImageError);
                    observer.unobserve(item.target);
                }
            });
        });

        $('img.lazy-load,img.lazy-load-carousel').each(async function(index) {
            const $this = $(this);
            observer.observe(this);
        });

        $('.lazy-load').on('load', async function() {
            const $this = $(this);

            $this.siblings('.lazyload-spinner-container').remove();
            $this.removeClass('lazy-load pull-left');
            clearTimeout(MayanImage.timer);
            MayanImage.timer = setTimeout(MayanImage.timerFunction, 50);
        });

        $('.lazy-load-carousel').on('load', async function() {
            const $this = $(this);

            $this.siblings('.lazyload-spinner-container').remove();
            $this.removeClass('lazy-load-carousel pull-left');
        });
    }

    static timerFunction () {
        $.fn.matchHeight._update();
    }
}

MayanImage.timer = setTimeout(null);

$.fn.matchHeight._maintainScroll = true;
