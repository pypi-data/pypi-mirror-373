{# templates/package_pkg_logical.tpl #}

<?xml version="1.0" encoding="utf-8"?>
<?AutomationStudio FileVersion="4.12"?>
<Package xmlns="http://br-automation.co.at/AS/Package">
  <Objects>
    <Object Type="Package" Description="Global libraries">Libraries</Object>
    {% for name in project_names %}
    <Object Type="Package">{{ name }}</Object>
    {% endfor %}
  </Objects>
</Package>
