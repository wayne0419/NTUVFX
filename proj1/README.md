# VFX Project 1: High Dynamic Range Imaging

## Author

- 網媒所 王哲瑋 Che Wei Wang r10944037


## Code Structure

- `run.sh`：run `main.py` with predefined arguments.
- `main.py`：will handle command line arguments and then `import lib` and `import utilities` to run the Debevec's HDR Method.
- `lib.py`：implementation of Debevec's Methods.
- `utilities.py`：handle some trivial functions，like `show_multiple_images`.


## How To Execute
- Data format:
	- Images should be named from 0 to N, where N is the number of your images.
	- ExposureTime should be stored in a file named exposures.txt , this file is not required if you have exposure time kept in your images' metadata.
- Execution methods:
	1. Execute `./code/run.sh` while in `./code`.
	2. Run `./code/main.py` with arguments:

|  Argument  |                         Explanation                          | Required |
| :--------: | :----------------------------------------------------------: | :------: |
| input_dir  |                 The directory where you put all your input images|   Yes    |
| image_extension | The extension of your image files | Yes |
| image_num | The number of your input images | Yes |
| exposure_path |            The path to your exposures.txt             | Optional |
| output_dir | The directory where you want to store all the outputs (including g_function plot, hdr file, tone_mapped hdr file with different parameters) |   Yes    |


## About The Algorithm

The algorithm being implemented in this project is Debevec's Method。

![img](./images/debevec.png)

After solving the gunction g in the above formula, I can use the below formula to calculate the radiance of every pixel.

![img](./images/debevec2.png)

This has to be done for every channel: R,G,B. In the end, we will get the radiance map for all three channels, and after stacking them together, we can get the HDR.

## 說明

我們大概拍了 9 張照片，其中 exposure 是每張照片兩倍的遞增。拿到 jpg 檔以後可以用 `PIL` 裡面的含式去讀 jpg 檔的 metadata 拿到 exposure （ see `lib.hdr.get_labeled_exif`）。這是 Debevec's Method 裡面的 delta t。

針對每一個 color channel（也就是接下來的步驟要總共做三次），要去 sample 圖中的一些點的 pixel value。我們最後是直接等距 sample 一些點，但試過 random sampling 其實效果也差不多。Sample 完點以後就是把值傳入 `lib.hdr.solve_debevec` 來解出 g 這個 mapping function（是一個 256 維的陣列，0~255 的 index 分別代表 該 pixel value 對應到的 irradiance 值）。

接者就可以用 g 來算不同 channel 的 radiance map。我們利用一些 numpy 中 vectorized 的函式（例如下面程式碼中的 `np.average`，可以加快速度：

```python
def get_radiance_map(images, g, exp, w):
    _h, _w = images[0].shape
    images = np.array(images)
    E = []
    for i, img in enumerate(images):
        E.append(g[img] - exp[i])
    rad = np.average(E, axis=0, weights=w[images])
    return rad
```

把三個 channel 的 radiance map 組合起來就可以得到最終的 hdr image。注意最後是用 `np.float32` 的資料型態來儲存。

最後我們利用開源的 Luminance HDR 套件來 tone map 我們的 hdr image，選用的演算法是 Mantuik '06。

## 結果

下面是我們拍攝的不同曝光時間的照片。

| ![img](./images/shifted/IMG_6538.JPG) | ![img](./images/shifted/IMG_6539.JPG) | ![img](./images/shifted/IMG_6540.JPG) |
| ------------------------------------- | ------------------------------------- | ------------------------------------- |
| ![img](./images/shifted/IMG_6541.JPG) | ![img](./images/shifted/IMG_6542.JPG) | ![img](./images/shifted/IMG_6543.JPG) |
| ![img](./images/shifted/IMG_6544.JPG) | ![img](./images/shifted/IMG_6545.JPG) | ![img](./images/shifted/IMG_6546.JPG) |

我們選用的參數是 lambda = 20，然後 weighting function 就是 linear（就是論文中提到的函式，後面會跟我們自己寫的 sin, guassian weighting 函式作比較）。

最終得到的不同 channel 的 mapping function g，可以看到幾乎是完全吻合，解出了同一個 g：

![img](./results/20.0_linear_align/exposure.png)

Tone mapped 的影像：

![img](./results/20.0_linear_align/result.png)

## 實驗

### 使用不同 Weighting Function

在 `lib.hat_functions` 中我們定義了一些對於 0 - 255 pixel 值的 weighting function，圖示如下：

![img](./images/hat.png)

實驗中，我們固定 lambda = 20，並使用 Mantuik '06 的演算法來 tone mapping，觀察 weighting function 對最終結果的影響，並把沒有 weighting 的當成對照組。

|          | g                                          | Tone mapped                              |
| -------- | ------------------------------------------ | ---------------------------------------- |
| None     | ![img](https://github.com/bchao1/High-Dynamic-Range-Imaging/blob/master/tests/20.0_none/exposure.png?raw=true)     | ![img](https://github.com/bchao1/High-Dynamic-Range-Imaging/blob/master/tests/20.0_none/result.png?raw=true)     |
| Linear   | ![img](./tests/20.0_linear/exposure.png)   | ![img](./tests/20.0_linear/result.png)   |
| Gaussian | ![img](./tests/20.0_gaussian/exposure.png) | ![img](./tests/20.0_gaussian/result.png) |
| Sin      | ![img](./tests/20.0_sin/exposure.png)      | ![img](./tests/20.0_sin/result.jpg)      |

其實結果並沒有差非常多。

###  使用不同 Lambda

我們嘗試使用不同的 lambda 來看看 objective 中平滑項和另一項的 tradeoff 關係。實驗中我們固定 weighting function 是 linear，並使用 Mantuik '06 來 tone map。

| Lambda | g                                        | Tone mapped                            |
| ------ | ---------------------------------------- | -------------------------------------- |
| 1      | ![img](./tests/1.0_linear/exposure.png)  | ![img](./tests/1.0_linear/result.png)  |
| 2      | ![img](./tests/2.0_linear/exposure.png)  | ![img](./tests/2.0_linear/result.png)  |
| 5      | ![img](./tests/5.0_linear/exposure.png)  | ![img](./tests/5.0_linear/result.png)  |
| 10     | ![img](./tests/10.0_linear/exposure.png) | ![img](./tests/10.0_linear/result.png) |
| 20     | ![img](./tests/20.0_linear/exposure.png) | ![img](./tests/20.0_linear/result.png) |
| 50     | ![img](./tests/50.0_linear/exposure.png) | ![img](./tests/50.0_linear/result.png) |

從上面的比較可以看出隨著 lambda 的增大，平滑項的影響也越來越大，因此曲線確實有越來越平滑。至於 tone mapped 以後的結果並無顯著的差別（但仔細觀察會發現 lambda 約大其實影像細節有比較清楚）。

### 使用 Alignment

我們也有另外時做了 MTB Alignment Algorithm，程式碼在 `lib.alignment`。下圖比較有無 alignment 的差別（我們固定 weight function 為 linear，lambda = 20）。  
我們實作Alignment的方法為MTB。首先我們先選定一張照片，以作為alignment的參考，這裡我們選定第五張照片，因為曝光太多或是太少的照片都會讓細節變得較少，不適合作為參考圖。  
選定照片之後，對於每一張照片，都套用MTB的方法來對齊照片。首先利用cv2中的resize功能，將要對齊的照片以及參考圖皆壓縮6倍（倍數可以調整），並將其轉會為bitmap，並搜尋其9個neighbors何者與參考圖的difference最小，並記錄下來。之後再將要對齊的照片壓縮5倍，並shift到上一層（壓縮6倍）時的最小difference位置，然後再搜尋其9個neighbors。重複至壓縮1倍（也就是沒有壓縮），並輸出shift過後的圖片。
這個方法的缺點是一但有一個level做錯，則後面就無法再shift回最佳的對齊位置了，且當圖片壓縮得越嚴重，則越有可能會shift錯位置，因此建議最大的壓縮倍數不要調得太高。

|                | Result                                            |
| -------------- | ------------------------------------------------- |
| No Alignment   | ![img](./results/20.0_linear_no_align/result.png) |
| With Alignment | ![img](./results/20.0_linear_align/result.png)    |

 