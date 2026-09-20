#/bin/bash

# snmp-server community password RO

PW=password

OID_CISCO_CPU=1.3.6.1.4.1.9.9.109.1.1.1.1.7
OID_ARISTA_CPU=1.3.6.1.2.1.25.3.3.1.2.1

HOSTS=(
  2600:bad:c0de::1,$OID_ARISTA_CPU
  2600:bad:c0de::2,$OID_ARISTA_CPU
  2600:bad:c0de::3,$OID_CISCO_CPU
  2600:bad:c0de::4,$OID_CISCO_CPU
  2600:bad:c0de::11,$OID_ARISTA_CPU
  2600:bad:c0de::12,$OID_ARISTA_CPU
  2600:bad:c0de::13,$OID_ARISTA_CPU
  2600:bad:c0de::14,$OID_ARISTA_CPU
)

for entry in "${HOSTS[@]}"; do
    host="${entry%%,*}"
    oid="${entry#*,}"
    snmpbulkwalk -v 2c -c $PW $host $oid 
done