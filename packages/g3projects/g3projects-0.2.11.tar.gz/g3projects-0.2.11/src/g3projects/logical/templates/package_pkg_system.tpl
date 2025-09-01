{# templates/package_pkg_system.tpl #}

<?xml version="1.0" encoding="utf-8"?>
<?AutomationStudio FileVersion="4.12"?>
<Package xmlns="http://br-automation.co.at/AS/Program">
  <Objects>
    <Object Type="File" Private="true">Zone.var</Object>
    <Object Type="Program" Language="ANSIC">Comm</Object>
    <Object Type="Program" Language="ANSIC">System</Object>
    {% for name in zone_names %}
    <Object Type="Program" Language="ANSIC">{{ name }}</Object>
    {% endfor %}
  </Objects>
</Package>
