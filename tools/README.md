# Weishaupt metadata dump

`dump_weishaupt_metadata.py` is a read-only diagnostic helper for checking
whether the local Weishaupt web interface documents additional hot-water mode,
hot-water enable/disable, or maintenance registers.

It only downloads:

- `/script/einstellung.js`
- `/script/Form_eth_log.js`
- `/sd/systable.csv`

It does not send CanApiJson `SET` commands and does not print credentials.

Example:

```powershell
$env:WEISHAUPT_PASSWORD = "Admin123"
python tools/dump_weishaupt_metadata.py --host 192.168.1.50 --output-dir weishaupt_metadata
```

After running it, inspect the files in `weishaupt_metadata/` for confirmed
register addresses before adding any new write entity.
