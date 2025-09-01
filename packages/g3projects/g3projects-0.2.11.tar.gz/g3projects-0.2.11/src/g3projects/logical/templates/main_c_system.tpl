{# templates/main_c_system.tpl #}

fbSystem.linkBackupConfig = &gSystemConfig;
fbSystem.linkBackupRemanentData = &gSystemData;
fbSystem.linkBackupEthernet = &gSystemEthernet;
fbSystem.linkBackupRoutingTable = &gRoutingTable;
fbSystem.linkBackupSHV = &gSHV;

fbSystem.dev = &System;
fSystem_System(&fbSystem);

{% if has_system_safety %}
fbSystemSafety.inSafeDomainLink = &gSafeDomain;
fbSystemSafety.dev = &SystemSafety;
fbSystemSafety.system = &System;
fSafety_SafetyCPU(&fbSystemSafety);
{% endif %}

{% if has_shv %}
fbSHV.dev = &SHV;
fbSHV.system = &System;
fSHV_TreeGlobal(&fbSHV);
{% endif %}

{% if has_elesys %}
fbELESYS.dev = &ELESYS;
fbELESYS.system = &System;
fElesys_Log(&fbELESYS);
{% endif %}
