{# templates/package_pkg_project.tpl #}

<?xml version="1.0" encoding="utf-8"?>
<?AutomationStudio FileVersion="4.12"?>
<Package xmlns="http://br-automation.co.at/AS/Package">
  <Objects>
    <Object Type="File">config.txt</Object>
    {% for name in system_names %}
    <Object Type="Package">{{ name }}</Object>
    {% endfor %}
  </Objects>
</Package>
