import os
import sys
import cv2
import pytest
from typing import List
import numpy as np

pytest_plugins = ('pytest_asyncio')

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from manga_translator.detection.textline_merge import dispatch as dispatch_merge
from manga_translator.utils import (
    TextBlock,
    Quadrilateral,
    visualize_textblocks,
)


BBOX_IMAGE_FOLDER = 'test/testdata/bboxes'
os.makedirs(BBOX_IMAGE_FOLDER, exist_ok=True)

def save_regions_to_image(path: str, regions: TextBlock, width: int, height: int):
    img = np.zeros((height, width, 3))
    cv2.imwrite(path, visualize_textblocks(img, regions))

def find_region_containing_line(line, regions):
    """
    Finds region index which contains the `line`.
    """
    for i, region in enumerate(regions):
        for rline in region.lines:
            if (line == rline).all():
                return i
    raise ValueError('regions do not contain line')

async def generate_combinations(lines: List[List[List[int]]], width: int, height: int):
    """
    Returns the line combination and regions generated by the textline merge.
    """
    regions = await dispatch_merge([Quadrilateral(np.array(line), '', 1) for line in lines], width, height)
    generated_combinations = []
    for region in regions:
        combination = []
        for rline in region.lines:
            for i, line in enumerate(lines):
                if (line == rline).all():
                    combination.append(i)
                    break
        combination.sort()
        generated_combinations.append(combination)
    return generated_combinations, regions

async def run_test(lines, expected_combinations, width, height, path = None):
    generated_combinations, regions = await generate_combinations(lines, width, height)

    # Save as image
    path = os.path.join(BBOX_IMAGE_FOLDER, path or 'bboxes.png')
    save_regions_to_image(path, regions, width, height)

    invalid_regions = []
    for i, generated_combination in enumerate(generated_combinations):
        if generated_combination not in expected_combinations:
            invalid_regions.append(i)
    if invalid_regions:
        raise Exception(f'Invalid regions: {invalid_regions} - Image saved under {path}')

        # # Search for all associated regions
        # associated_regions = []
        # similar_expected_combination = None
        # for combination in expected_combinations:
        #     if generated_combination[0] in combination:
        #         similar_expected_combination = combination
        #         break
        # assert similar_expected_combination is not None
        # for j in similar_expected_combination:
        #     ri = find_region_containing_line(lines[j], regions)
        #     if ri and ri not in associated_regions:
        #         associated_regions.append(ri)

        # raise Exception(f'Regions: {associated_regions} should be merged - Image saved under {path}')


@pytest.mark.asyncio
async def test_merge_image1(): # demo/image/original3.jpg
    width, height = 2590, 4096
    lines = [
        [[   0, 3280], [ 237, 3234], [ 394, 4069], [ 149, 4096]],
        [[2400, 3210], [2493, 3210], [2498, 4061], [2405, 4061]],
        [[2306, 3208], [2410, 3208], [2416, 3992], [2312, 3992]],
        [[2226, 3208], [2328, 3208], [2328, 4050], [2226, 4050]],
        [[2149, 3205], [2242, 3205], [2237, 4005], [2144, 4005]],
        [[2160, 2298], [2245, 2298], [2250, 3069], [2165, 3069]],
        [[2082, 2296], [2176, 2296], [2176, 3032], [2082, 3032]],
        [[2008, 2293], [2109, 2293], [2109, 2680], [2008, 2680]],
        [[ 162, 1733], [ 256, 1733], [ 256, 2141], [ 162, 2141]],
        [[ 242, 1733], [ 336, 1733], [ 336, 2144], [ 242, 2144]],
        [[2269, 1349], [2368, 1349], [2373, 1960], [2274, 1960]],
        [[2186, 1352], [2288, 1352], [2288, 1760], [2186, 1760]],
        [[2373, 1357], [2442, 1357], [2442, 2077], [2373, 2077]],
        [[ 536, 1349], [ 613, 1349], [ 613, 1997], [ 536, 1997]],
        [[ 594, 1344], [ 680, 1344], [ 696, 2072], [ 610, 2072]],
        [[1037,  485], [1282,  469], [1349, 1418], [1104, 1434]],
        [[ 234,  528], [ 312,  528], [ 312, 1176], [ 234, 1176]],
        [[ 138,  509], [ 256,  509], [ 256,  706], [ 138,  706]],
        [[2418,  384], [2504,  384], [2509, 1234], [2424, 1234]],
        [[2344,  381], [2429,  381], [2434,  965], [2349,  965]],
        [[2269,  376], [2370,  376], [2370,  818], [2269,  818]],
        [[ 197,   42], [2405,   37], [2405,  362], [ 197,  368]],
    ]
    expected_combinations = [[0], [1, 2, 3, 4], [5, 6, 7], [8, 9], [10, 11, 12], [13, 14], [15], [16, 17], [18, 19, 20], [21]]
    await run_test(lines, expected_combinations, width, height, '1.png')
    
@pytest.mark.asyncio
async def test_merge_image1_upscaled(): # demo/image/original3.jpg upscaled x2
    width, height = 5180, 8192
    # detector has picked up less textlines
    lines = [
        [[   5, 6698], [ 506, 6602], [ 794, 8133], [ 293, 8192]],
        [[4800, 6421], [4986, 6421], [4997, 8122], [4810, 8122]],
        [[4618, 6416], [4821, 6416], [4837, 7984], [4634, 7984]],
        [[4453, 6416], [4656, 6416], [4656, 8096], [4453, 8096]],
        [[4298, 6410], [4485, 6410], [4474, 8010], [4288, 8010]],
        [[4309, 4592], [4496, 4592], [4512, 6144], [4325, 6144]],
        [[4165, 4592], [4352, 4592], [4352, 6064], [4165, 6064]],
        [[4016, 4586], [4218, 4586], [4218, 5360], [4016, 5360]],
        [[ 330, 3472], [ 517, 3472], [ 517, 4288], [ 330, 4288]],
        [[ 485, 3466], [ 672, 3466], [ 672, 4293], [ 485, 4293]],
        [[4544, 2704], [4730, 2704], [4741, 3909], [4554, 3909]],
        [[4373, 2704], [4576, 2704], [4576, 3520], [4373, 3520]],
        [[4746, 2714], [4885, 2714], [4885, 4149], [4746, 4149]],
        [[1072, 2709], [1226, 2709], [1226, 4000], [1072, 4000]],
        [[1189, 2693], [1360, 2693], [1392, 4138], [1221, 4138]],
        [[ 469, 1050], [ 624, 1050], [ 624, 2352], [ 469, 2352]],
        [[ 277, 1018], [ 512, 1018], [ 512, 1413], [ 277, 1413]],
        [[4837,  768], [5008,  768], [5018, 2469], [4848, 2469]],
        [[4688,  762], [4858,  762], [4869, 1930], [4698, 1930]],
        [[4538,  757], [4730,  757], [4741, 1632], [4549, 1632]],
        [[ 474,   80], [4805,   80], [4805,  730], [ 474,  730]],
    ]
    print((await generate_combinations(lines, width, height))[0])
    expected_combinations = [[0], [1, 2, 3, 4], [5, 6, 7], [8, 9], [10, 11, 12], [13, 14], [15, 16], [17, 18, 19], [20]]
    await run_test(lines, expected_combinations, width, height, '1_upscaled.png')

@pytest.mark.asyncio
async def test_merge_image2():
    width, height = 1317, 1637
    lines = [
        [[ 555, 1327], [ 609, 1311], [ 641, 1423], [ 588, 1439]],
        [[ 588, 1297], [ 637, 1285], [ 665, 1396], [ 616, 1407]],
        [[ 229, 1033], [ 280, 1019], [ 303, 1107], [ 252, 1121]],
        [[ 265,  996], [ 311,  992], [ 318, 1078], [ 272, 1082]],
        [[  65,  953], [ 111,  950], [ 149, 1434], [ 102, 1437]],
        [[ 119,  947], [ 169,  944], [ 219, 1579], [ 169, 1582]],
        [[1218,  894], [1271,  899], [1234, 1251], [1180, 1245]],
        [[1156,  886], [1219,  893], [1158, 1441], [1095, 1435]],
        [[1243,  201], [1305,  213], [1190,  800], [1128,  788]],
        [[1181,  189], [1246,  201], [1185,  557], [1120,  545]],
        [[1130,  180], [1190,  191], [1090,  686], [1030,  674]],
        [[1075,  169], [1133,  181], [1025,  718], [ 966,  706]],
        [[1009,  154], [1076,  166], [1033,  422], [ 966,  410]],
        [[ 960,  142], [1023,  155], [ 910,  694], [ 847,  682]],
        [[ 742,   31], [ 804,   38], [ 759,  489], [ 698,  482]],
        [[ 688,   26], [ 744,   33], [ 669,  720], [ 612,  714]],
        [[ 624,   14], [ 686,   21], [ 629,  573], [ 568,  566]],
        [[ 566,    9], [ 629,   15], [ 585,  473], [ 522,  466]],
    ]
    expected_combinations = [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9, 10, 11, 12, 13], [14, 15, 16, 17]]
    await run_test(lines, expected_combinations, width, height, '2.png')

@pytest.mark.asyncio
async def test_merge_image3():
    width, height = 1920, 1360
    lines = [
        [[  46,  467], [ 103,  462], [ 158, 1122], [ 101, 1127]],
        [[1651,  322], [1703,  318], [1716,  512], [1663,  516]],
        [[1702,  317], [1756,  315], [1778,  748], [1725,  751]],
        [[1758,  313], [1810,  311], [1825,  638], [1773,  641]],
        [[ 752,  261], [ 800,  265], [ 775,  525], [ 727,  521]],
        [[ 471,  228], [ 528,  221], [ 627,  935], [ 570,  942]],
        [[1243,  128], [1631,  101], [1688,  888], [1301,  916]],
        [[ 540,  215], [ 597,  207], [ 681,  812], [ 623,  820]],
        [[ 592,  181], [ 662,  166], [ 715,  412], [ 645,  427]],
        [[ 852,  107], [ 903,  101], [ 962,  633], [ 911,  640]],
        [[ 223,   97], [ 288,   97], [ 297,  936], [ 232,  936]],
        [[1816,   45], [1885,   50], [1862,  345], [1793,  340]],
        [[1745,   42], [1815,   43], [1808,  346], [1738,  345]],
    ]
    expected_combinations = [[0], [10], [1, 2, 3], [11, 12], [5, 7, 8], [4], [9], [6]]
    await run_test(lines, expected_combinations, width, height, '3.png')
    
@pytest.mark.asyncio
async def test_merge_image4(): # Issue #215
    width, height = 800, 1280
    lines = [
        [[ 467, 1074], [ 614, 1073], [ 614, 1110], [ 467, 1111]],
        [[ 484, 1041], [ 600, 1041], [ 600, 1081], [ 484, 1081]],
        [[ 358,  952], [ 515,  952], [ 515,  989], [ 358,  989]],
        [[ 351,  920], [ 513,  920], [ 513,  956], [ 351,  956]],
        [[ 378,  886], [ 484,  886], [ 484,  926], [ 378,  926]],
        [[ 388,  852], [ 477,  856], [ 475,  895], [ 386,  891]],
        [[ 164,  629], [ 298,  628], [ 298,  668], [ 164,  669]],
        [[ 184,  594], [ 270,  594], [ 270,  640], [ 184,  640]],
        [[ 149,  563], [ 305,  562], [ 305,  605], [ 149,  605]],
        [[ 127,  532], [ 330,  532], [ 330,  571], [ 127,  571]],
        [[ 179,  497], [ 274,  495], [ 275,  541], [ 180,  543]],
    ]
    # print((await generate_combinations(lines, width, height))[0])
    expected_combinations = [[0, 1], [2, 3, 4, 5], [6, 7, 8, 9, 10]]
    await run_test(lines, expected_combinations, width, height, '4.png')
