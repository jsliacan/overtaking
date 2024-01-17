# overtaking

Python project with code analyzing overtaking distances.

The assumption is that the data are structured as shared, but `BikeLogs` folder is placed in `$(HOME)/Downloads`. If not the case, modify `constants.py` so that `DATA_HOME` variable is the expansion of the correct location. Use `~` for `$(HOME)` (user's home dir).

## Example
From date `20230112`.

Data from the box (classification: -1 oncoming, 1 overtaking, 0 didn't find any significant dip in lat distance). Same output can by obtained by running `python3 box.py`.
```
classification,flag,press_length,date_string,timestamp,event_start,interval_length,interval
-1,0,5,20230112,18:49:38,20907,5,"[439, 439, 441, 449, 449]"
1,0,30,20230112,18:49:59,21354,15,"[314, 302, 299, 297, 299, 299, 299, 299, 297, 297, 294, 297, 302, 307, 396]"
-1,1,9,20230112,18:51:53,23755,6,"[304, 304, 304, 307, 330, 535]"
1,0,27,20230112,18:54:45,27390,8,"[314, 312, 309, 309, 309, 299, 309, 309]"
-1,0,4,20230112,18:59:20,33174,5,"[325, 317, 320, 320, 325]"
1,0,26,20230112,18:59:37,33526,11,"[297, 292, 289, 289, 289, 289, 289, 289, 294, 312, 459]"
-1,0,6,20230112,19:00:51,35101,3,"[335, 332, 335]"
-1,0,5,20230112,19:05:57,41521,5,"[279, 256, 259, 261, 269]"
-1,0,6,20230112,19:09:49,46420,5,"[411, 302, 297, 294, 299]"
1,0,29,20230112,19:12:39,49997,10,"[182, 170, 170, 167, 160, 167, 167, 167, 165, 170]"
-1,0,5,20230112,19:16:34,54928,6,"[398, 264, 220, 182, 223, 238]"
-1,0,6,20230112,19:18:10,56952,5,"[187, 187, 185, 187, 195]"
-1,0,3,20230112,19:20:06,59389,6,"[243, 236, 231, 231, 233, 248]"
-1,1,9,20230112,19:20:43,60180,5,"[215, 208, 205, 205, 210]"
-1,0,5,20230112,19:28:13,69646,5,"[375, 365, 365, 370, 391]"
-1,0,5,20230112,19:28:16,69706,5,"[391, 368, 368, 368, 375]"
1,2,9,20230112,19:48:17,94962,1,[365]
```

Data from the radar. Can be obtained by running `python3 radar.py`. Each timestamp stands for incremented radar counter.

```
1 2023-01-12 18:36:51+00:00
2 2023-01-12 18:43:53+00:00
3 2023-01-12 18:45:52+00:00
4 2023-01-12 18:46:40+00:00
5 2023-01-12 18:50:04+00:00
6 2023-01-12 18:51:39+00:00
7 2023-01-12 18:54:49+00:00
8 2023-01-12 18:59:41+00:00
9 2023-01-12 19:12:43+00:00
10 2023-01-12 19:32:04+00:00
11 2023-01-12 19:32:08+00:00
12 2023-01-12 19:32:30+00:00
13 2023-01-12 19:32:34+00:00
14 2023-01-12 19:32:42+00:00
15 2023-01-12 19:33:17+00:00
16 2023-01-12 19:33:19+00:00
17 2023-01-12 19:33:30+00:00
18 2023-01-12 19:34:04+00:00
19 2023-01-12 19:35:09+00:00
20 2023-01-12 19:37:07+00:00
```
