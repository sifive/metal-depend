{% extends "base.lds" %}

{% block description %}
/* RAM Read-Only Data Linker Script
 *
 * This linker script places application code and read-only data into writable
 * memories in an attempt to improve performance, since writable memories
 * are generally lower-latency. This linker script may cause your application
 * to overflow RAM, since it dramatically increases the quantity of data vying
 * for space there.
 */
{% endblock %}

{#
 # Set layout options
 #}
{% set ramrodata = True %}
