from unittest.mock import MagicMock, patch

import pytest

from libdc3.services.caf.client import CAF


@pytest.fixture
def caf_collisions22_html_response():
    return """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<html>
 <head>
  <title>Index of /CAF/certification/Collisions22</title>
 </head>
 <body>
<h1>Index of /CAF/certification/Collisions22</h1>
<pre><img src="/_shared_static_content/icons/blank.gif" alt="Icon "> <a href="?C=N;O=D">Name</a>                                               <a href="?C=M;O=A">Last modified</a>      <a href="?C=S;O=A">Size</a>  <a href="?C=D;O=A">Description</a><hr><img src="/_shared_static_content/icons/back.gif" alt="[PARENTDIR]"> <a href="/CAF/certification/">Parent Directory</a>                                                        -
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022A_352416_354787_Muon.json">Cert_Collisions2022A_352416_354787_Muon.json</a>       2022-12-01 07:22  471
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_362760_Golden.json">Cert_Collisions2022_355100_362760_Golden.json</a>      2023-01-24 08:01  9.9K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_362760_Muon.json">Cert_Collisions2022_355100_362760_Muon.json</a>        2023-01-25 13:55   12K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_eraB_355100_355769_Golden.json">Cert_Collisions2022_eraB_355100_355769_Golden.json</a> 2023-01-24 10:33  459
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_eraB_355100_355769_Muon.json">Cert_Collisions2022_eraB_355100_355769_Muon.json</a>   2023-01-24 06:58  1.1K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_eraC_355862_357482_Golden.json">Cert_Collisions2022_eraC_355862_357482_Golden.json</a> 2023-01-24 10:33  2.8K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_eraC_355862_357482_Muon.json">Cert_Collisions2022_eraC_355862_357482_Muon.json</a>   2023-01-24 10:33  3.5K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_eraD_357538_357900_Golden.json">Cert_Collisions2022_eraD_357538_357900_Golden.json</a> 2023-01-24 10:34  1.1K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_eraD_357538_357900_Muon.json">Cert_Collisions2022_eraD_357538_357900_Muon.json</a>   2023-01-24 10:34  1.5K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_eraE_359022_360331_Golden.json">Cert_Collisions2022_eraE_359022_360331_Golden.json</a> 2022-11-30 11:43  1.7K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_eraE_359022_360331_Muon.json">Cert_Collisions2022_eraE_359022_360331_Muon.json</a>   2022-11-17 18:16  1.7K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_eraF_360390_362167_Golden.json">Cert_Collisions2022_eraF_360390_362167_Golden.json</a> 2022-12-08 10:48  3.1K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_eraF_360390_362167_Muon.json">Cert_Collisions2022_eraF_360390_362167_Muon.json</a>   2022-12-08 12:27  3.2K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_eraG_362433_362760_Golden.json">Cert_Collisions2022_eraG_362433_362760_Golden.json</a> 2023-01-24 07:45  738
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_eraG_362433_362760_Muon.json">Cert_Collisions2022_eraG_362433_362760_Muon.json</a>   2023-01-24 07:43  791
<img src="/_shared_static_content/icons/folder.gif" alt="[DIR]"> <a href="Collisions2022HISpecial/">Collisions2022HISpecial/</a>                           2023-01-24 09:01    -
<img src="/_shared_static_content/icons/folder.gif" alt="[DIR]"> <a href="DCSOnly_JSONS/">DCSOnly_JSONS/</a>                                     2025-05-08 10:24    -
<img src="/_shared_static_content/icons/folder.gif" alt="[DIR]"> <a href="PileUp/">PileUp/</a>                                            2024-01-10 16:45    -
<img src="/_shared_static_content/icons/folder.gif" alt="[DIR]"> <a href="PromptReco/">PromptReco/</a>                                        2023-12-22 11:56    -
<img src="/_shared_static_content/icons/folder.gif" alt="[DIR]"> <a href="Run2logic_jsons/">Run2logic_jsons/</a>                                   2022-11-17 15:38    -
<img src="/_shared_static_content/icons/folder.gif" alt="[DIR]"> <a href="Run3logic_jsons_obsolete/">Run3logic_jsons_obsolete/</a>                          2023-01-27 16:23    -
<img src="/_shared_static_content/icons/p.gif" alt="[   ]"> <a href="compareJSON.py">compareJSON.py</a>                                     2023-09-26 18:35  2.8K
<img src="/_shared_static_content/icons/folder.gif" alt="[DIR]"> <a href="csv_files/">csv_files/</a>                                         2025-05-08 10:24    -
<hr></pre>
</body></html>
"""


@pytest.fixture
def caf_collisions22_dcs_html_response():
    return """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<html>
 <head>
  <title>Index of /CAF/certification/Collisions22/DCSOnly_JSONS/dailyDCSOnlyJSON</title>
 </head>
 <body>
<h1>Index of /CAF/certification/Collisions22/DCSOnly_JSONS/dailyDCSOnlyJSON</h1>
<pre><img src="/_shared_static_content/icons/blank.gif" alt="Icon "> <a href="?C=N;O=D">Name</a>                                                        <a href="?C=M;O=A">Last modified</a>      <a href="?C=S;O=A">Size</a>  <a href="?C=D;O=A">Description</a><hr><img src="/_shared_static_content/icons/back.gif" alt="[PARENTDIR]"> <a href="/CAF/certification/Collisions22/DCSOnly_JSONS/">Parent Directory</a>                                                                 -
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022A_352417_353709_900GeV_DCSOnly_TkPx.json">Cert_Collisions2022A_352417_353709_900GeV_DCSOnly_TkPx.json</a> 2022-10-13 20:11  1.7K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_355208_13p6TeV_DCSOnly.json">Cert_Collisions2022_355100_355208_13p6TeV_DCSOnly.json</a>      2022-07-11 23:55  2.3K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_355208_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_355208_13p6TeV_DCSOnly_TkPx.json</a> 2022-07-12 11:28  1.2K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_355559_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_355559_13p6TeV_DCSOnly_TkPx.json</a> 2022-07-14 19:12  2.2K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_355680_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_355680_13p6TeV_DCSOnly_TkPx.json</a> 2022-07-15 18:32  2.3K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_355769_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_355769_13p6TeV_DCSOnly_TkPx.json</a> 2022-07-18 18:30  2.3K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_355862_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_355862_13p6TeV_DCSOnly_TkPx.json</a> 2022-07-27 10:27  2.3K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_355913_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_355913_13p6TeV_DCSOnly_TkPx.json</a> 2022-07-27 10:26  2.5K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_355942_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_355942_13p6TeV_DCSOnly_TkPx.json</a> 2022-07-27 10:28  2.6K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_356048_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_356048_13p6TeV_DCSOnly_TkPx.json</a> 2022-07-27 10:26  3.0K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_356135_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_356135_13p6TeV_DCSOnly_TkPx.json</a> 2022-07-27 10:25  3.2K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_356175_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_356175_13p6TeV_DCSOnly_TkPx.json</a> 2022-07-27 10:25  3.4K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_356371_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_356371_13p6TeV_DCSOnly_TkPx.json</a> 2022-07-28 21:59  3.5K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_356427_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_356427_13p6TeV_DCSOnly_TkPx.json</a> 2022-07-29 22:36  3.7K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_356476_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_356476_13p6TeV_DCSOnly_TkPx.json</a> 2022-07-30 22:17  4.2K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_356614_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_356614_13p6TeV_DCSOnly_TkPx.json</a> 2022-08-03 02:15  4.8K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_356619_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_356619_13p6TeV_DCSOnly_TkPx.json</a> 2022-08-03 21:14  4.9K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_356722_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_356722_13p6TeV_DCSOnly_TkPx.json</a> 2022-08-04 20:06  5.0K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_356970_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_356970_13p6TeV_DCSOnly_TkPx.json</a> 2022-08-08 15:19  5.7K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_357081_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_357081_13p6TeV_DCSOnly_TkPx.json</a> 2022-08-09 18:45  6.0K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_357112_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_357112_13p6TeV_DCSOnly_TkPx.json</a> 2022-08-10 18:31  6.3K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_357328_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_357328_13p6TeV_DCSOnly_TkPx.json</a> 2022-08-12 00:21  6.3K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_357550_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_357550_13p6TeV_DCSOnly_TkPx.json</a> 2022-08-16 07:35  6.8K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_357611_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_357611_13p6TeV_DCSOnly_TkPx.json</a> 2022-08-17 16:01  6.8K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_357688_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_357688_13p6TeV_DCSOnly_TkPx.json</a> 2022-08-19 09:20  6.9K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_357734_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_357734_13p6TeV_DCSOnly_TkPx.json</a> 2022-08-20 20:01  7.3K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_357771_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_357771_13p6TeV_DCSOnly_TkPx.json</a> 2022-08-21 23:58  7.5K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_357815_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_357815_13p6TeV_DCSOnly_TkPx.json</a> 2022-08-23 00:35  7.9K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_357900_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_357900_13p6TeV_DCSOnly_TkPx.json</a> 2022-08-23 19:40  8.3K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_359899_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_359899_13p6TeV_DCSOnly_TkPx.json</a> 2022-10-06 16:31  9.5K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_360090_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_360090_13p6TeV_DCSOnly_TkPx.json</a> 2022-10-10 17:14   10K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_360225_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_360225_13p6TeV_DCSOnly_TkPx.json</a> 2022-10-12 13:07   10K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_360296_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_360296_13p6TeV_DCSOnly_TkPx.json</a> 2022-10-13 19:21   10K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_360400_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_360400_13p6TeV_DCSOnly_TkPx.json</a> 2022-10-15 09:57   10K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_360458_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_360458_13p6TeV_DCSOnly_TkPx.json</a> 2022-10-16 11:55   11K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_360491_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_360491_13p6TeV_DCSOnly_TkPx.json</a> 2022-10-17 14:54   11K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_360761_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_360761_13p6TeV_DCSOnly_TkPx.json</a> 2022-10-19 21:22   11K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_360819_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_360819_13p6TeV_DCSOnly_TkPx.json</a> 2022-10-20 21:05   11K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_360992_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_360992_13p6TeV_DCSOnly_TkPx.json</a> 2022-10-24 15:26   12K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_361083_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_361083_13p6TeV_DCSOnly_TkPx.json</a> 2022-10-25 18:26   12K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_361239_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_361239_13p6TeV_DCSOnly_TkPx.json</a> 2022-10-28 12:25   12K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_361443_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_361443_13p6TeV_DCSOnly_TkPx.json</a> 2022-11-03 12:10   13K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_361580_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_361580_13p6TeV_DCSOnly_TkPx.json</a> 2022-11-07 13:34   13K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_361957_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_361957_13p6TeV_DCSOnly_TkPx.json</a> 2022-11-12 17:57   13K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_361994_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_361994_13p6TeV_DCSOnly_TkPx.json</a> 2022-11-14 06:18   13K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_362106_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_362106_13p6TeV_DCSOnly_TkPx.json</a> 2022-11-16 07:11   14K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_362167_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_362167_13p6TeV_DCSOnly_TkPx.json</a> 2022-11-17 18:04   14K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355100_362618_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355100_362618_13p6TeV_DCSOnly_TkPx.json</a> 2022-11-24 17:01   15K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2022_355374_355559_13p6TeV_DCSOnly_TkPx.json">Cert_Collisions2022_355374_355559_13p6TeV_DCSOnly_TkPx.json</a> 2022-07-13 18:15  1.0K
<hr></pre>
</body></html>
    """


@pytest.fixture
def caf_collisions24_html_response():
    return """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<html>
 <head>
  <title>Index of /CAF/certification/Collisions24</title>
 </head>
 <body>
<h1>Index of /CAF/certification/Collisions24</h1>
<pre><img src="/_shared_static_content/icons/blank.gif" alt="Icon "> <a href="?C=N;O=D">Name</a>                                                <a href="?C=M;O=A">Last modified</a>      <a href="?C=S;O=A">Size</a>  <a href="?C=D;O=A">Description</a><hr><img src="/_shared_static_content/icons/back.gif" alt="[PARENTDIR]"> <a href="/CAF/certification/">Parent Directory</a>                                                         -
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="2024B_Golden.json">2024B_Golden.json</a>                                   2024-10-29 12:16  1.2K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="2024B_Muon.json">2024B_Muon.json</a>                                     2024-10-29 12:16  1.3K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="2024C_Golden.json">2024C_Golden.json</a>                                   2024-10-29 12:16  3.7K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="2024C_Muon.json">2024C_Muon.json</a>                                     2024-10-29 12:16  3.4K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="2024D_Golden.json">2024D_Golden.json</a>                                   2024-10-29 12:16  3.2K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="2024D_Muon.json">2024D_Muon.json</a>                                     2024-10-29 12:16  3.3K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="2024E_Golden.json">2024E_Golden.json</a>                                   2024-10-29 12:16  3.9K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="2024E_Muon.json">2024E_Muon.json</a>                                     2024-10-29 12:16  3.7K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="2024F_Golden.json">2024F_Golden.json</a>                                   2024-10-29 12:16   11K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="2024F_Muon.json">2024F_Muon.json</a>                                     2024-10-29 12:16  9.5K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="2024G_Golden.json">2024G_Golden.json</a>                                   2024-10-29 12:16   13K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="2024G_Muon.json">2024G_Muon.json</a>                                     2024-10-29 12:16   11K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="2024H_Golden.json">2024H_Golden.json</a>                                   2024-10-29 12:16  1.7K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="2024H_Muon.json">2024H_Muon.json</a>                                     2024-10-29 12:16  1.7K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="2024I_Golden.json">2024I_Golden.json</a>                                   2024-10-29 12:16  4.5K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="2024I_Muon.json">2024I_Muon.json</a>                                     2024-10-29 12:16  3.7K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2024_378981_386951_Golden.json">Cert_Collisions2024_378981_386951_Golden.json</a>       2024-12-19 16:31   44K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2024_378981_386951_Muon.json">Cert_Collisions2024_378981_386951_Muon.json</a>         2024-12-19 16:31   39K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2024_ppref_387474_387574_DCS.json">Cert_Collisions2024_ppref_387474_387574_DCS.json</a>    2024-11-09 15:31  291
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2024_ppref_387474_387574_Muon.json">Cert_Collisions2024_ppref_387474_387574_Muon.json</a>   2024-11-09 14:52  291
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2024_ppref_387474_387721_DCS.json">Cert_Collisions2024_ppref_387474_387721_DCS.json</a>    2024-11-19 17:36  561
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2024_ppref_387474_387721_Muon.json">Cert_Collisions2024_ppref_387474_387721_Muon.json</a>   2024-11-15 16:14  631
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Cert_Collisions2024_ppref_387474_387721_golden.json">Cert_Collisions2024_ppref_387474_387721_golden.json</a> 2024-11-28 20:49  693
<img src="/_shared_static_content/icons/folder.gif" alt="[DIR]"> <a href="DCSOnly_JSONS/">DCSOnly_JSONS/</a>                                      2025-05-08 10:24    -
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="LowPU.json">LowPU.json</a>                                          2024-10-29 12:06  229
<img src="/_shared_static_content/icons/folder.gif" alt="[DIR]"> <a href="outToDate/">outToDate/</a>                                          2024-12-19 16:30    -
<img src="/_shared_static_content/icons/folder.gif" alt="[DIR]"> <a href="testoutput/">testoutput/</a>                                         2025-05-08 10:24    -
<hr></pre>
</body></html>

"""


@pytest.fixture
def caf_collisions24_dcs_html_response():
    return """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN">
<html>
 <head>
  <title>Index of /CAF/certification/Collisions24/DCSOnly_JSONS/dailyDCSOnlyJSON</title>
 </head>
 <body>
<h1>Index of /CAF/certification/Collisions24/DCSOnly_JSONS/dailyDCSOnlyJSON</h1>
<pre><img src="/_shared_static_content/icons/blank.gif" alt="Icon "> <a href="?C=N;O=D">Name</a>                                                       <a href="?C=M;O=A">Last modified</a>      <a href="?C=S;O=A">Size</a>  <a href="?C=D;O=A">Description</a><hr><img src="/_shared_static_content/icons/back.gif" alt="[PARENTDIR]"> <a href="/CAF/certification/Collisions24/DCSOnly_JSONS/">Parent Directory</a>                                                                -
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24Special_900GeV_378238_378239_DCSOnly_TkPx.json">Collisions24Special_900GeV_378238_378239_DCSOnly_TkPx.json</a> 2024-03-26 13:01  552
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24Special_900GeV_378238_378751_DCSOnly_TkPx.json">Collisions24Special_900GeV_378238_378751_DCSOnly_TkPx.json</a> 2024-11-05 16:16  629
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24Special_900GeV_Latest.json">Collisions24Special_900GeV_Latest.json</a>                     2024-11-05 16:16  629
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_5p36TeV_387474_387721_DCSOnly_TkPx.json">Collisions24_5p36TeV_387474_387721_DCSOnly_TkPx.json</a>       2024-11-05 16:20  1.3K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_5p36TeV_Latest.json">Collisions24_5p36TeV_Latest.json</a>                           2024-11-05 16:20  1.3K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_379075_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_379075_DCSOnly_TkPx.json</a>       2024-04-08 19:31  1.2K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_379154_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_379154_DCSOnly_TkPx.json</a>       2024-04-10 19:31  1.3K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_379253_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_379253_DCSOnly_TkPx.json</a>       2024-04-11 19:30  1.4K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_379338_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_379338_DCSOnly_TkPx.json</a>       2024-04-12 19:31  1.5K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_379355_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_379355_DCSOnly_TkPx.json</a>       2024-04-14 19:31  1.6K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_379454_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_379454_DCSOnly_TkPx.json</a>       2024-04-15 19:31  1.7K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_379470_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_379470_DCSOnly_TkPx.json</a>       2024-04-16 19:30  1.8K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_379530_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_379530_DCSOnly_TkPx.json</a>       2024-04-17 19:31  1.8K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_379618_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_379618_DCSOnly_TkPx.json</a>       2024-04-18 19:31  1.9K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_379661_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_379661_DCSOnly_TkPx.json</a>       2024-04-19 19:31  2.0K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_379729_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_379729_DCSOnly_TkPx.json</a>       2024-04-20 19:31  2.0K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_379774_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_379774_DCSOnly_TkPx.json</a>       2024-04-23 19:31  2.1K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_379866_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_379866_DCSOnly_TkPx.json</a>       2024-04-25 19:31  2.1K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_380029_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_380029_DCSOnly_TkPx.json</a>       2024-04-26 19:31  2.2K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_380050_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_380050_DCSOnly_TkPx.json</a>       2024-04-27 19:31  2.4K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_380074_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_380074_DCSOnly_TkPx.json</a>       2024-04-29 19:31  2.5K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_380128_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_380128_DCSOnly_TkPx.json</a>       2024-04-30 19:31  2.6K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_380197_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_380197_DCSOnly_TkPx.json</a>       2024-05-01 19:31  2.7K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_380238_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_380238_DCSOnly_TkPx.json</a>       2024-05-02 19:31  2.7K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_380310_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_380310_DCSOnly_TkPx.json</a>       2024-05-03 19:30  2.9K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_380349_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_380349_DCSOnly_TkPx.json</a>       2024-05-04 19:31  2.9K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_380384_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_380384_DCSOnly_TkPx.json</a>       2024-05-05 19:31  3.0K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_380403_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_380403_DCSOnly_TkPx.json</a>       2024-05-06 19:31  3.1K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_380466_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_380466_DCSOnly_TkPx.json</a>       2024-05-07 19:31  3.2K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_380481_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_380481_DCSOnly_TkPx.json</a>       2024-05-08 19:31  3.2K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_380533_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_380533_DCSOnly_TkPx.json</a>       2024-05-09 19:31  3.4K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_380567_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_380567_DCSOnly_TkPx.json</a>       2024-05-11 19:31  3.6K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_380627_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_380627_DCSOnly_TkPx.json</a>       2024-05-12 19:30  3.7K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_380649_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_380649_DCSOnly_TkPx.json</a>       2024-05-17 19:31  3.8K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_380883_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_380883_DCSOnly_TkPx.json</a>       2024-05-19 19:31  3.8K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_380933_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_380933_DCSOnly_TkPx.json</a>       2024-05-20 19:30  3.8K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_380963_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_380963_DCSOnly_TkPx.json</a>       2024-05-21 19:31  3.9K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_381053_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_381053_DCSOnly_TkPx.json</a>       2024-05-22 19:31  3.9K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_381080_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_381080_DCSOnly_TkPx.json</a>       2024-05-23 19:31  4.1K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_381150_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_381150_DCSOnly_TkPx.json</a>       2024-05-24 19:31  4.3K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_381164_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_381164_DCSOnly_TkPx.json</a>       2024-05-25 19:31  4.4K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_381199_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_381199_DCSOnly_TkPx.json</a>       2024-05-26 19:31  4.5K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_381212_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_381212_DCSOnly_TkPx.json</a>       2024-05-27 19:31  4.5K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_381309_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_381309_DCSOnly_TkPx.json</a>       2024-05-28 19:31  4.5K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_381379_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_381379_DCSOnly_TkPx.json</a>       2024-05-29 19:31  4.6K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_381380_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_381380_DCSOnly_TkPx.json</a>       2024-05-30 19:31  4.7K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_381384_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_381384_DCSOnly_TkPx.json</a>       2024-05-31 19:31  4.7K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_381417_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_381417_DCSOnly_TkPx.json</a>       2024-06-01 19:31  4.7K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_381478_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_381478_DCSOnly_TkPx.json</a>       2024-06-02 19:31  4.8K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_381484_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_381484_DCSOnly_TkPx.json</a>       2024-06-03 19:31  4.8K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_381516_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_381516_DCSOnly_TkPx.json</a>       2024-06-04 19:32  4.9K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_381544_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_381544_DCSOnly_TkPx.json</a>       2024-06-05 19:31  5.0K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_381594_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_381594_DCSOnly_TkPx.json</a>       2024-06-19 19:31  5.0K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_382229_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_382229_DCSOnly_TkPx.json</a>       2024-06-20 19:31  5.0K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_382262_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_382262_DCSOnly_TkPx.json</a>       2024-06-21 19:31  5.2K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_382314_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_382314_DCSOnly_TkPx.json</a>       2024-06-22 19:31  5.3K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_382329_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_382329_DCSOnly_TkPx.json</a>       2024-06-23 19:31  5.4K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_382344_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_382344_DCSOnly_TkPx.json</a>       2024-06-26 19:31  5.4K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_382504_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_382504_DCSOnly_TkPx.json</a>       2024-06-28 19:31  5.5K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_382568_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_382568_DCSOnly_TkPx.json</a>       2024-06-29 19:31  5.5K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_382595_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_382595_DCSOnly_TkPx.json</a>       2024-06-30 19:30  5.6K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_382617_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_382617_DCSOnly_TkPx.json</a>       2024-07-01 12:02  5.6K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_382626_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_382626_DCSOnly_TkPx.json</a>       2024-07-01 19:31  5.6K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_382656_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_382656_DCSOnly_TkPx.json</a>       2024-07-02 19:31  5.7K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_382686_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_382686_DCSOnly_TkPx.json</a>       2024-07-03 19:31  5.8K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_382749_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_382749_DCSOnly_TkPx.json</a>       2024-07-04 19:31  5.9K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_382769_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_382769_DCSOnly_TkPx.json</a>       2024-07-05 19:31  6.0K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_382811_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_382811_DCSOnly_TkPx.json</a>       2024-07-06 19:31  6.2K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_382834_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_382834_DCSOnly_TkPx.json</a>       2024-07-07 19:31  6.2K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_382878_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_382878_DCSOnly_TkPx.json</a>       2024-07-08 19:31  6.3K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_382913_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_382913_DCSOnly_TkPx.json</a>       2024-07-09 19:31  6.3K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_382960_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_382960_DCSOnly_TkPx.json</a>       2024-07-10 19:31  6.5K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_383036_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_383036_DCSOnly_TkPx.json</a>       2024-07-12 19:30  6.6K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_383154_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_383154_DCSOnly_TkPx.json</a>       2024-07-13 19:30  6.7K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_383162_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_383162_DCSOnly_TkPx.json</a>       2024-07-14 19:31  6.7K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_383175_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_383175_DCSOnly_TkPx.json</a>       2024-07-15 19:30  6.8K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_383254_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_383254_DCSOnly_TkPx.json</a>       2024-07-16 19:31  6.9K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_383277_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_383277_DCSOnly_TkPx.json</a>       2024-07-17 19:31  6.9K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_383366_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_383366_DCSOnly_TkPx.json</a>       2024-07-18 19:31  7.2K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_383377_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_383377_DCSOnly_TkPx.json</a>       2024-07-19 19:31  7.3K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_383418_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_383418_DCSOnly_TkPx.json</a>       2024-07-20 19:31  7.3K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_383467_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_383467_DCSOnly_TkPx.json</a>       2024-07-21 19:31  7.4K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_383949_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_383949_DCSOnly_TkPx.json</a>       2024-08-02 19:31  8.7K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_384031_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_384031_DCSOnly_TkPx.json</a>       2024-08-03 19:31  8.8K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_384052_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_384052_DCSOnly_TkPx.json</a>       2024-08-04 19:32  8.9K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_384071_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_384071_DCSOnly_TkPx.json</a>       2024-08-05 19:31  9.0K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_384128_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_384128_DCSOnly_TkPx.json</a>       2024-08-06 19:30  9.1K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_384188_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_384188_DCSOnly_TkPx.json</a>       2024-08-07 19:31  9.1K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_384209_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_384209_DCSOnly_TkPx.json</a>       2024-08-08 19:31  9.2K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_384244_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_384244_DCSOnly_TkPx.json</a>       2024-08-09 19:31  9.3K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_384265_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_384265_DCSOnly_TkPx.json</a>       2024-08-10 19:31  9.4K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_384318_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_384318_DCSOnly_TkPx.json</a>       2024-08-11 19:31  9.5K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_384332_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_384332_DCSOnly_TkPx.json</a>       2024-08-12 19:32  9.6K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_384383_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_384383_DCSOnly_TkPx.json</a>       2024-08-13 19:31  9.7K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_384446_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_384446_DCSOnly_TkPx.json</a>       2024-08-14 19:31  9.7K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_384491_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_384491_DCSOnly_TkPx.json</a>       2024-08-15 19:31  9.9K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_384492_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_384492_DCSOnly_TkPx.json</a>       2024-08-16 19:31   10K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_384579_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_384579_DCSOnly_TkPx.json</a>       2024-08-17 19:32   10K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_384614_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_384614_DCSOnly_TkPx.json</a>       2024-08-18 19:31   10K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_384644_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_384644_DCSOnly_TkPx.json</a>       2024-08-23 19:31   10K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_384950_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_384950_DCSOnly_TkPx.json</a>       2024-08-24 19:31   10K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_384963_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_384963_DCSOnly_TkPx.json</a>       2024-08-25 19:31   10K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_385012_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_385012_DCSOnly_TkPx.json</a>       2024-08-26 19:31   10K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_385016_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_385016_DCSOnly_TkPx.json</a>       2024-08-28 19:31   10K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_385100_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_385100_DCSOnly_TkPx.json</a>       2024-08-29 19:31   10K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_385134_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_385134_DCSOnly_TkPx.json</a>       2024-08-30 19:31   11K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_385153_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_385153_DCSOnly_TkPx.json</a>       2024-08-31 19:31   11K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_385178_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_385178_DCSOnly_TkPx.json</a>       2024-09-01 19:31   11K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_385194_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_385194_DCSOnly_TkPx.json</a>       2024-09-02 19:31   11K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_385260_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_385260_DCSOnly_TkPx.json</a>       2024-09-03 19:31   11K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_385286_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_385286_DCSOnly_TkPx.json</a>       2024-09-04 19:31   11K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_385324_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_385324_DCSOnly_TkPx.json</a>       2024-09-05 19:31   11K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_385384_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_385384_DCSOnly_TkPx.json</a>       2024-09-06 19:31   11K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_385391_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_385391_DCSOnly_TkPx.json</a>       2024-09-07 19:31   11K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_385423_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_385423_DCSOnly_TkPx.json</a>       2024-09-08 19:32   11K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_385447_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_385447_DCSOnly_TkPx.json</a>       2024-09-09 19:31   11K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_385514_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_385514_DCSOnly_TkPx.json</a>       2024-09-10 19:31   11K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_385568_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_385568_DCSOnly_TkPx.json</a>       2024-09-11 19:31   12K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_385619_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_385619_DCSOnly_TkPx.json</a>       2024-09-12 19:31   12K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_385697_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_385697_DCSOnly_TkPx.json</a>       2024-09-13 19:31   12K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_385727_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_385727_DCSOnly_TkPx.json</a>       2024-09-14 19:31   12K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_385754_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_385754_DCSOnly_TkPx.json</a>       2024-09-15 19:31   12K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_385801_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_385801_DCSOnly_TkPx.json</a>       2024-09-16 19:31   12K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_385885_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_385885_DCSOnly_TkPx.json</a>       2024-09-17 19:31   12K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_385908_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_385908_DCSOnly_TkPx.json</a>       2024-09-18 19:31   12K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_385934_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_385934_DCSOnly_TkPx.json</a>       2024-09-19 19:31   12K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_386008_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_386008_DCSOnly_TkPx.json</a>       2024-09-20 19:31   13K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_386025_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_386025_DCSOnly_TkPx.json</a>       2024-09-21 19:31   13K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_386047_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_386047_DCSOnly_TkPx.json</a>       2024-09-22 19:31   13K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_386071_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_386071_DCSOnly_TkPx.json</a>       2024-09-25 19:31   13K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_386313_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_386313_DCSOnly_TkPx.json</a>       2024-09-26 19:30   13K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_386319_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_386319_DCSOnly_TkPx.json</a>       2024-10-01 19:30   13K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_386478_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_386478_DCSOnly_TkPx.json</a>       2024-10-02 19:30   13K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_386509_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_386509_DCSOnly_TkPx.json</a>       2024-10-03 19:31   13K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_386592_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_386592_DCSOnly_TkPx.json</a>       2024-10-04 19:31   13K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_386594_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_386594_DCSOnly_TkPx.json</a>       2024-10-05 19:31   13K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_386630_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_386630_DCSOnly_TkPx.json</a>       2024-10-06 19:31   13K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_386661_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_386661_DCSOnly_TkPx.json</a>       2024-10-07 19:31   13K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_386693_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_386693_DCSOnly_TkPx.json</a>       2024-10-08 19:31   13K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_386705_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_386705_DCSOnly_TkPx.json</a>       2024-10-09 19:31   13K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_386795_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_386795_DCSOnly_TkPx.json</a>       2024-10-10 19:31   13K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_386814_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_386814_DCSOnly_TkPx.json</a>       2024-10-11 19:31   14K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_386863_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_386863_DCSOnly_TkPx.json</a>       2024-10-12 19:31   14K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_386873_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_386873_DCSOnly_TkPx.json</a>       2024-10-13 19:31   14K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_386885_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_386885_DCSOnly_TkPx.json</a>       2024-10-14 19:31   14K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_386925_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_386925_DCSOnly_TkPx.json</a>       2024-10-15 19:31   14K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_378981_386951_DCSOnly_TkPx.json">Collisions24_13p6TeV_378981_386951_DCSOnly_TkPx.json</a>       2024-11-05 16:15   23K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_Latest.json">Collisions24_13p6TeV_Latest.json</a>                           2024-11-05 16:15   23K
<img src="/_shared_static_content/icons/unknown.gif" alt="[   ]"> <a href="Collisions24_13p6TeV_forPdMVProd.json">Collisions24_13p6TeV_forPdMVProd.json</a>                      2024-11-05 16:15   23K
<hr></pre>
</body></html>
    """


@patch("libdc3.services.caf.client.CAF._CAF__get_retry_forbidden")
def test_corner_case_2022_caf_muon_options_and_latest(mock_get, caf_collisions22_html_response):
    mock_response = MagicMock()
    mock_response.text = caf_collisions22_html_response
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    caf = CAF("Collisions22", "muon")
    assert len(caf.options) == 8
    assert caf.latest["name"] == "Cert_Collisions2022_355100_362760_Muon.json"
    assert caf.latest["size"] == "12K"


@patch("libdc3.services.caf.client.CAF._CAF__get_retry_forbidden")
def test_corner_case_2022_caf_golden_options_and_latest(mock_get, caf_collisions22_html_response):
    mock_response = MagicMock()
    mock_response.text = caf_collisions22_html_response
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    caf = CAF("Collisions22", "golden")
    assert len(caf.options) == 7
    assert caf.latest["name"] == "Cert_Collisions2022_eraD_357538_357900_Golden.json"
    assert caf.latest["size"] == "1.1K"


@patch("libdc3.services.caf.client.CAF._CAF__get_retry_forbidden")
def test_corner_case_2022_caf_dcs_options_and_latest(mock_get, caf_collisions22_dcs_html_response):
    mock_response = MagicMock()
    mock_response.text = caf_collisions22_dcs_html_response
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    caf = CAF("Collisions22", "dcs")
    assert len(caf.options) == 48
    assert caf.latest["name"] == "Cert_Collisions2022_355100_362618_13p6TeV_DCSOnly_TkPx.json"
    assert caf.latest["size"] == "15K"


@patch("libdc3.services.caf.client.CAF._CAF__get_retry_forbidden")
def test_caf_muon_options_and_latest(mock_get, caf_collisions24_html_response):
    mock_response = MagicMock()
    mock_response.text = caf_collisions24_html_response
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    caf = CAF("Collisions24", "muon")
    assert len(caf.options) == 3
    assert caf.latest["name"] == "Cert_Collisions2024_378981_386951_Muon.json"
    assert caf.latest["size"] == "39K"


@patch("libdc3.services.caf.client.CAF._CAF__get_retry_forbidden")
def test_caf_golden_options_and_latest(mock_get, caf_collisions24_html_response):
    mock_response = MagicMock()
    mock_response.text = caf_collisions24_html_response
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    caf = CAF("Collisions24", "golden")
    assert len(caf.options) == 1
    assert caf.latest["name"] == "Cert_Collisions2024_378981_386951_Golden.json"
    assert caf.latest["size"] == "44K"


@patch("libdc3.services.caf.client.CAF._CAF__get_retry_forbidden")
def test_caf_dcs_options_and_latest(mock_get, caf_collisions24_dcs_html_response):
    mock_response = MagicMock()
    mock_response.text = caf_collisions24_dcs_html_response
    mock_response.raise_for_status = MagicMock()
    mock_get.return_value = mock_response

    caf = CAF("Collisions24", "dcs")
    assert len(caf.options) == 145
    assert caf.latest["name"] == "Collisions24_5p36TeV_387474_387721_DCSOnly_TkPx.json"
    assert caf.latest["size"] == "1.3K"


@patch("libdc3.services.caf.client.CAF._CAF__get_retry_forbidden")
def test_download_latest(mock_get, caf_collisions24_html_response):
    # First call: options, Second call: download
    mock_response_options = MagicMock()
    mock_response_options.text = caf_collisions24_html_response
    mock_response_options.raise_for_status = MagicMock()

    mock_response_download = MagicMock()
    mock_response_download.raise_for_status = MagicMock()
    mock_response_download.json.return_value = {"foo": "bar"}

    mock_get.side_effect = [mock_response_options, mock_response_download]

    caf = CAF("Collisions2024", "golden")
    data = caf.download(latest=True)
    assert data == {"foo": "bar"}
    assert mock_get.call_count == 2


@patch("libdc3.services.caf.client.CAF._CAF__get_retry_forbidden")
def test_download_by_name(mock_get, caf_collisions24_html_response):
    mock_response_options = MagicMock()
    mock_response_options.text = caf_collisions24_html_response
    mock_response_options.raise_for_status = MagicMock()

    mock_response_download = MagicMock()
    mock_response_download.raise_for_status = MagicMock()
    mock_response_download.json.return_value = {"baz": "qux"}

    mock_get.side_effect = [mock_response_options, mock_response_download]

    caf = CAF("Collisions2024", "golden")
    name = "Cert_Collisions2024_378981_386951_Golden.json"
    data = caf.download(name=name)
    assert data == {"baz": "qux"}
    assert mock_get.call_count == 2


@patch("libdc3.services.caf.client.CAF._CAF__get_retry_forbidden")
def test_download_invalid_name_raises(mock_get, caf_collisions24_html_response):
    mock_response_options = MagicMock()
    mock_response_options.text = caf_collisions24_html_response
    mock_response_options.raise_for_status = MagicMock()
    mock_get.return_value = mock_response_options

    caf = CAF("Collisions2024", "golden")
    with pytest.raises(StopIteration):
        caf.download(name="nonexistent.json")
