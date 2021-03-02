
import sqlite3

def exec(sql):
	db = sqlite3.connect("./logfiles.sql")
	dbcur = db.cursor()
	dbcur.execute(sql)
	db.commit()
	db.close()


# empty database
exec('DELETE FROM log')

r = [	[	"$CPDIR/log/cpd.elg",	"sk102975",	"SIC Error for LSMServerAddon: Got alert from peer that the certificate expired"	],
	[	"$CPDIR/log/cpd.elg",	"sk102975",	"Renew_SIC_Cert_cb: CPD failed to renew sic certificate. status = 3, rc - -1"	],
	[	"$CPDIR/log/cpd.elg",	"sk164255",	"Renew_SIC_Cert_cb: CPD failed to renew sic certificate. status = 3, rc - -1"	],
	[	"$CPDIR/log/cpd.elg",	"sk119894",	"(0x86ed7f8) failed (0) No SIC error message"	],
	[	"$CPDIR/log/cpd.elg",	"sk119894",	"fwasync_do_mux_in:"	],
	[	"$FWDIR/log/fwm.elg",	"sk119894",	"fwasync_do_mux_in:"	],
	[	"$CPDIR/log/cpd.elg",	"sk119894",	"Not communicating. Authentication error [error no. 147]"	],
	[	"$CPDIR/log/cpd.elg",	"sk166902",	"br_names: failed to close pipe"	],
	[	"$CPDIR/log/cpd.elg",	"sk162435",	"SIC Error: illegal client sic name"],
	[	"$CPDIR/log/cpd.elg",	"sk135492",	"Renew_SIC_Cert_cb: CPD failed to renew sic certificate. status = 1, rc - -1"	],
	[	"$CPDIR/log/cpd.elg",	"sk168674",	"Warning:cp_timed_blocker_handler: A handler [0xf128ae90] blocked for"	],
	[	"$FWDIR/log/fwd.elg",	"sk37030",	"fwsyncn_connected: connection to"	],
	[	"$FWDIR/log/fwd.elg",	"sk102422",	"fwarp_get_arp_interface: no interface found on same subnet as valid ip address"	],
	[	"$FWDIR/log/fwd.elg",	"sk172086",	"status to Status ERROR description: Log-Server Disconnected"	],
	[	"$FWDIR/log/fw.elg",	"sk122172",	"fwdgxsam_init(): gx_sam_proxy_create failed"	],
	[	"$FWDIR/log/fwd.elg",	"sk153772",	"CFwdAlertsHandler::execute: failed to execute SEND_TO_SYS_STAT command"	],
	[	"$INDEXERDIR/log/log_indexer.elg", "sk116117", "CBinaryLogFile::ReplaceFileToMemStringID: error"	],
	[	"$INDEXERDIR/log/log_indexer.elg", "sk116117", "find Interface Name string id, will set to NULL"	],
	[	"$FWDIR/log/fwd.elg",	"sk105246",	"fwd: restarting vpnd"	],
	[	"$FWDIR/log/fwd.elg",	"sk100551",	"cpdict_add_entry: fail to alloc: Cannot allocate memory lvtrack_parse"	],
	[	"$FWDIR/log/fwd.elg",	"sk100551",	"No such file or directory"	],
	[	"$FWDIR/log/fwd.elg",	"sk146152",	"logbuf_write: writes logs to local disk because overflow"	],
	[	"$FWDIR/log/fwd.elg",	"sk146152",	"no diskspace left, stopped logging"	],
	[	"$FWDIR/log/fwd.elg",	"sk30154",	"new interface was installed: configuration"	],
	[	"$FWDIR/log/fwd.elg",	"sk30154",	"fwarp_initialize_myself: unable to find mac address of interface"	],
	[	"$FWDIR/log/fwd.elg",	"sk37665",	"cpobj_swsam_amt_enabled: can"	],
	[	"$FWDIR/log/fwm.elg",	"sk82420",	"Too many open files"	]	]


for row in r:
	print("Adding row: " + row[2])
	exec("INSERT INTO log (logfile, sk, message) VALUES ('"+row[0]+"','"+row[1]+"','"+row[2]+"')")
