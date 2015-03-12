<?php

$stats = array();
foreach($this->DS as $KEY=>$VAL) {
	if(true !== strpos($VAL["NAME"], "-")) {
		list($kind, $interface) = explode("-", $VAL["NAME"]);
		if(!array_key_exists($interface, $stats)) {
			$stats[$interface] = array();
		}
		$stats[$interface][$kind] = $VAL;
	}
}

function labels($var, $aggr, $text) {
	$ret = "";
	foreach($aggr as $key=>$func) {
		$ret .= "GPRINT:$var:$func:\"$text";
		if($key + 1 == sizeof($aggr)) {
			$ret .= '\\l" ';
		} else {
			$ret .= ' " ';
		}
	}
	return $ret;
}

foreach($stats as $interface=>$ifacestat) {
	$ds_name["$interface-bytes"] = "$interface-bytes";
	$opt["$interface-bytes"] = '--vertical-label Bytes --title "' . $this->MACRO['DISP_HOSTNAME'] . ' / ' . $interface . ' Bytes"';
	$def["$interface-bytes"] = "";
	if(array_key_exists("out", $ifacestat)) {
		$def["$interface-bytes"] .= rrd::def("out", $VAL['RRDFILE'], $ifacestat["out"]['DS'], "AVERAGE");
	}
	if(array_key_exists("in", $ifacestat)) {
		$def["$interface-bytes"] .= rrd::def("posin", $VAL['RRDFILE'], $ifacestat["in"]['DS'], "AVERAGE");
		$def["$interface-bytes"] .= "CDEF:in=posin,-1,* ";
	}
	$def["$interface-bytes"] .= 'COMMENT:"             Max           Avg          Last\\l" ';
	$aggrs = array("MAX", "AVERAGE", "LAST");
	if(array_key_exists("in", $ifacestat)) {
		$def["$interface-bytes"] .= 'AREA:in#008800:"In   " ';
		$def["$interface-bytes"] .= labels("posin", $aggrs, "%6.1lf %SB/s");
	}
	if(array_key_exists("out", $ifacestat)) {
		$def["$interface-bytes"] .= 'AREA:out#00cc00:"Out  " ';
		$def["$interface-bytes"] .= labels("out", $aggrs, "%6.1lf %SB/s");
	}
}

?>
