{# templates/variables_var_system.tpl #}

fbSystem : fSystem_System;

{% if has_system_safety %}
fbSystemSafety : fSafety_SafetyCPU;
{% endif %}

{% if has_shv %}
fbSHV : fSHV_TreeGlobal;
{% endif %}

{% if has_elesys %}
fbELESYS : fElesys_Log;
{% endif %}
