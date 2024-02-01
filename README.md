# overtaking

Python project with code analyzing overtaking distances.

The assumption is that the data is structured as follows:

``` text
BikeLogs
	|---- 20221218
	|          |--- 20221218_ANALOG18.TXT
	|          |--- 20221218_Forerunner645.fit
	|          |--- 20221218_Wahoo.fit
	|---- 20230116
	|          |--- 20230116_ANALOG18.TXT
	|          |--- 20230116_Forerunner645.fit
	|          |--- 20230116_Wahoo.fit
```

and that the `BikeLogs` folder is located in `$(HOME)/Downloads`. If you want your `BikeLogs` folder elsewhere, modify values in `src/constants.py`.

## Example

Clone this project and navigate to it

``` bash
$ git clone https://github.com/jsliacan/overtaking.git
$ cd overtaking
```
From here, you can type `python3 .` to run the script in `__main__.py`. The uncommented section will run `collate_event()` and print them one by one.

## Events

The list of events looks a follows:

``` csv
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
```

