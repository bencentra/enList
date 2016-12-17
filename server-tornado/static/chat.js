var updater = {
  socket: null,

  init: function () {
    var url = "ws://" + location.host + "/chatsocket";
    updater.socket = new WebSocket(url);
    updater.socket.onmessage = function (e) {
      updater.showMessage(JSON.parse(e.data));
    }
  },

  showMessage: function (message) {
    var existing = $('#m' + message.id);
    if (existing.length > 0) return;
    var node = $(message.html);
    $('#inbox').append(node);
  }
};

var form = {
  $form: null,

  newMessage: function () {
    var message = form.formToDict();
    updater.socket.send(JSON.stringify(message));
    $('input[type="text"]').val('').select();
  },

  formToDict: function () {
    var fields = form.$form.serializeArray();
    var json = {};
    for (var i = 0; i < fields.length; i++) {
      json[fields[i].name] = fields[i].value;
    }
    if (json.next) delete json.next;
    return json;
  },

  init: function ($el) {
    form.$form = $($el);
    form.$form.on('submit', function (e) {
      e.preventDefault();
      form.newMessage();
      return false;
    });
    form.$form.on('keypress', function (e) {
      if (e.keyCode === 13) {
        form.newMessage();
        return false;
      }
    });
  }
}

$(document).ready(function () {
  var $form = $('#messageform');
  form.init($form);
  $('#message').select();
  updater.init();
});
