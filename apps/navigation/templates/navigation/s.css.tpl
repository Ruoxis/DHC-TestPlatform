{% load static %}
@font-face {
  font-family: 'MyIcons';
  src: url('{% static "fonts/my-icons.woff2" %}') format('woff2');
}

.my-icon-twitter::before {
  font-family: 'MyIcons';
  content: "\e001"; /* 你的图标字符代码 */
}
/* 动态CSS模板 */
.header {
    background-color: {{ theme_color|default:'#333' }};
    background-image: url("{% static 'app1/images/bg.png' %}");
}
/* 使用Django模板语法 */
.logo {
    background-image: url("{% static 'myapp/images/logo.png' %}");
    font-family: "CustomFont";
    src: url("{% static 'myapp/fonts/custom.woff2' %}") format('woff2');
}
