# Mining Software Download Instructions

This directory should contain the mining software executables. The GPU Mining Suite supports multiple miners but requires you to download them separately due to licensing restrictions.

## Supported Miners

### 1. T-Rex Miner (Recommended for NVIDIA)
**Best for:** RVN, ETC, ERG

- **Download:** https://github.com/trex-miner/T-Rex/releases
- **Latest Version:** v0.26.8+
- **File:** Extract `t-rex.exe` to this directory
- **Features:** Excellent for KawPow, Ethash, Autolykos2
- **Fee:** 1%

### 2. lolMiner
**Best for:** FLUX, KAS, ALPH

- **Download:** https://github.com/Lolliedieb/lolMiner-releases/releases
- **Latest Version:** v1.82+
- **File:** Extract `lolMiner.exe` to this directory
- **Features:** Great for ZelHash, kHeavyHash, Blake3
- **Fee:** 0.7-1%

### 3. GMiner (Alternative)
**Alternative option for most algorithms**

- **Download:** https://github.com/develsoftware/GMinerRelease/releases
- **Latest Version:** v3.44+
- **File:** Extract `miner.exe` to this directory
- **Fee:** 1-2.5%

## Installation Steps

1. **Choose your miner(s)** based on the coins you want to mine
2. **Download** the latest release from the links above
3. **Extract** the archive to a temporary location
4. **Copy the executable(s)** to this `miners/` directory:
   - T-Rex: `t-rex.exe`
   - lolMiner: `lolMiner.exe`
   - GMiner: `miner.exe`
5. **Done!** The GPU Mining Suite will automatically detect and use them

## Example Directory Structure

```
miners/
├── README.md (this file)
├── t-rex.exe
├── lolMiner.exe
└── miner.exe (optional)
```

## Coin to Miner Mapping

The system will automatically choose the best miner for each coin:

- **RVN (Ravencoin)** → T-Rex Miner
- **ETC (Ethereum Classic)** → T-Rex Miner
- **ERG (Ergo)** → T-Rex Miner
- **FLUX** → lolMiner
- **KAS (Kaspa)** → lolMiner
- **ALPH (Alephium)** → lolMiner

## Security Notes

⚠️ **Important Security Information:**

1. **Download from official sources only** - Use the GitHub links provided above
2. **Verify checksums** - Check SHA256 hashes when available
3. **Windows Defender** may flag mining software as potentially unwanted programs (PUP) - this is normal for miners but add exceptions carefully
4. **Antivirus** software often blocks miners - you may need to add exceptions
5. **Never download** mining software from untrusted sources

## Antivirus/Windows Defender

Mining software is often flagged by antivirus programs. To add exceptions:

### Windows Defender
1. Open Windows Security
2. Go to "Virus & threat protection"
3. Click "Manage settings" under "Virus & threat protection settings"
4. Scroll to "Exclusions" and click "Add or remove exclusions"
5. Add the `miners/` folder

### Other Antivirus
Consult your antivirus documentation for adding folder exclusions.

## Troubleshooting

### Miner Not Found Error
- Ensure the executable is in the `miners/` directory
- Check the filename matches exactly (case-sensitive on some systems)
- Verify the file is not quarantined by antivirus

### Miner Crashes Immediately
- Check if your GPU supports the algorithm
- Ensure your NVIDIA drivers are up to date (470+)
- Try running the miner manually first to see error messages
- Check if the miner has dependencies (Visual C++ Redistributable)

### Permission Denied
- Run as Administrator
- Check that the file is not blocked (Right-click → Properties → Unblock)

## Dependencies

Some miners may require:
- **Visual C++ Redistributable 2015-2022** (x64)
  - Download: https://aka.ms/vs/17/release/vc_redist.x64.exe

## License Information

Each mining software has its own license:
- **T-Rex Miner**: Proprietary (1% dev fee)
- **lolMiner**: Proprietary (0.7-1% dev fee)
- **GMiner**: Proprietary (1-2.5% dev fee)

Please review each miner's license terms before use.

## Need Help?

If you encounter issues:
1. Check the miner's GitHub issues page
2. Verify your configuration in `configs/settings.json`
3. Check logs in the `logs/` directory
4. See the main README.md troubleshooting section

---

**Remember:** You are responsible for complying with all local laws and regulations regarding cryptocurrency mining.
