(function () {
  'use strict';

  var AB = new Backbone.Marionette.Application();

  AB.addRegions({
    content: '#content',
  });

  AB.addInitializer(function (options) {
    var srv = new SiteResultsView({
      collection: options.results,
    });

    AB.content.show(srv);
  });

  var SiteResult = Backbone.Model.extend({
  });

  var SiteResults = Backbone.Collection.extend({
    model: SiteResult,
  });

  var SiteResultView = Backbone.Marionette.ItemView.extend({
    template: '#tpl-siteresult',
    tagName: 'tr',
    className: 'siteresult'
  });

  var SiteResultsView = Backbone.Marionette.CompositeView.extend({
    tagName: 'table',
    id: 'siteresults',
    className: 'table table-striped table-bordered',
    template: '#tpl-siteresults',
    childView: SiteResultView,
  });

  AB.start({
    results: new SiteResults([
      {
        name: 'site_1',
      },
    ]),
  });

})();
