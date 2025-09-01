#!/usr/bin/env python
# coding=utf-8
# @Time    : 2021/3/5 11:18
# @Author  : 江斌
# @Software: PyCharm
import json
import msgpack
from struct import pack, unpack
import lz4.block as lz4

LZ4_HEAD = b'xmovlz4'
VALID_MODES = b'bcfu'
START = len(LZ4_HEAD) + 1 + 4


class MessageCompress(object):
    @staticmethod
    def compress_by_msgpack(msg):
        """
        使用msgpack压缩数据。
        :param msg: 原始消息，dict类型。
        :return: msgpack压缩后的消息，byte类型。
        """
        data_msgpack = msgpack.packb(msg, use_single_float=True, use_bin_type=True)
        return data_msgpack

    @staticmethod
    def decompress_msgpack(data):
        msg = msgpack.unpackb(data)
        return msg

    @staticmethod
    def compress_by_lz4(msg):
        """
        使用msgpack和lz4压缩消息。
        具体步骤:
        (1) 使用msgpack对msg进行pack得到data_msgpack
        (2) 使用lz4对data_msgpack进行压缩得到data_msgpack_lz4， data_msgpack_lz4包含四字节长度是解压后的消息长度（store_size=True）。
        (3) 在data_msgpack_lz4头部添加xmov头标识。

        数据结构：
                [标志头][捕捉类型][时间戳][解压后长度][消息体]
        字节数：  7       1         4        4         N
        类型：   char     char      float    int       char
        内容：   xmovlz4  f/b/c/u
        :param msg: 原始消息，dict类型。
        :return: 压缩后的消息，字节类型。
        """
        data_msgpack = msgpack.packb(msg, use_single_float=True, use_bin_type=True)
        data_msgpack_lz4 = lz4.compress(data_msgpack, mode='default', store_size=True)  # store_size=True自带解压后长度
        # length = len(data_msgpack_lz4).to_bytes(4, byteorder='little')
        mode = msg.get('data_type', 'u')[0].encode()  # 首字母
        ts = msg.get('data', msg).get('XCTimeStamp', '0')
        ts = float(ts)
        time_stamp = pack('<f', ts)  # 小端模式

        data_compressed = LZ4_HEAD + mode + time_stamp + data_msgpack_lz4
        return data_compressed

    @staticmethod
    def decompress_by_lz4(compressed_data):
        head = compressed_data[0:len(LZ4_HEAD)]
        mode = compressed_data[len(LZ4_HEAD):(len(LZ4_HEAD)+1)]
        assert head == LZ4_HEAD, f'无效的lz4压缩消息, 头标识不是{LZ4_HEAD}'
        assert mode in VALID_MODES, f'无效的消息模式，模式必须为：B/C/F三者之一'
        # uncompressed_data_len = int.from_bytes(compressed_data[start:(start+4)], byteorder='little')
        data_msgpack = lz4.decompress(compressed_data[START:])  # python自动会识别解压后长度
        msg = msgpack.unpackb(data_msgpack)
        return msg

    @staticmethod
    def unpack_header(compressed_data):
        head = compressed_data[0:len(LZ4_HEAD)]
        mode = compressed_data[len(LZ4_HEAD):(len(LZ4_HEAD)+1)]  # b/c/f/u
        assert head == LZ4_HEAD, f'无效的lz4压缩消息, 头标识不是{LZ4_HEAD}'
        assert mode in VALID_MODES, f'无效的消息模式，模式必须为：b/c/f三者之一'
        header = dict(
            prefix=LZ4_HEAD.decode(),
            mode=mode.decode(),
            timestamp=unpack('<f', compressed_data[(len(LZ4_HEAD) + 1):(len(LZ4_HEAD) + 5)])[0]
        )
        return header


# pack_msg = MessageCompress.compress_by_msgpack
pack_msg = MessageCompress.compress_by_lz4  # 使用lz4进行消息压缩


def test_compress_by_lz4():
    """
    body_msg是一帧动捕重定向后发送至UE4的消息。
    :return:
    """
    body_msg = {'XCTimeStamp': '22.9259033',
                'skeleton_frame': {'Ankle_L': {'Rotate': [-0.050906114280223846,
                                                          -0.01059131883084774,
                                                          0.10674119740724564,
                                                          0.9929263591766357]},
                                   'Ankle_R': {'Rotate': [0.05194775387644768,
                                                          0.047911711037158966,
                                                          0.08773936331272125,
                                                          0.9936335682868958]},
                                   'ChestEnd_M': {'Rotate': [0.0, 0.0, 0.0, 1.0]},
                                   'Chest_M': {'Rotate': [0.0, 0.0, 0.0, 1.0]},
                                   'Cup_L': {'Rotate': [0.001747839734889567,
                                                        -0.03137010708451271,
                                                        -0.0556030310690403,
                                                        0.9979584813117981]},
                                   'Cup_R': {'Rotate': [0.001747839734889567,
                                                        -0.03137010708451271,
                                                        -0.0556030310690403,
                                                        0.9979584813117981]},
                                   'ElbowPart1_L': {'Rotate': [-0.07271866500377655,
                                                               0.0,
                                                               0.0,
                                                               0.9973524808883667]},
                                   'ElbowPart1_R': {'Rotate': [-0.10048821568489075,
                                                               0.0,
                                                               0.0,
                                                               0.9949382543563843]},
                                   'ElbowPart2_L': {'Rotate': [-0.07271866500377655,
                                                               0.0,
                                                               0.0,
                                                               0.9973524808883667]},
                                   'ElbowPart2_R': {'Rotate': [-0.10048821568489075,
                                                               0.0,
                                                               0.0,
                                                               0.9949382543563843]},
                                   'Elbow_L': {'Rotate': [0.0018259754870086908,
                                                          0.008043680340051651,
                                                          -0.2746523320674896,
                                                          0.9615082144737244]},
                                   'Elbow_R': {'Rotate': [0.00214049918577075,
                                                          0.00942689273506403,
                                                          -0.3184100389480591,
                                                          0.9479038119316101]},
                                   'HeadEnd_M': {'Rotate': [0.0, 0.0, 0.0, 1.0]},
                                   'Head_M': {'Rotate': [0.018732210621237755,
                                                         0.017917705699801445,
                                                         0.054843537509441376,
                                                         0.9981584548950195]},
                                   'HipPart1_L': {'Rotate': [0.0, 0.0, 0.0, 1.0]},
                                   'HipPart1_R': {'Rotate': [0.0, 0.0, 0.0, 1.0]},
                                   'HipPart2_L': {'Rotate': [0.0, 0.0, 0.0, 1.0]},
                                   'HipPart2_R': {'Rotate': [0.0, 0.0, 0.0, 1.0]},
                                   'Hip_L': {'Rotate': [0.9888270497322083,
                                                        0.13545668125152588,
                                                        0.061889275908470154,
                                                        0.006495961919426918]},
                                   'Hip_R': {'Rotate': [0.17157971858978271,
                                                        0.9805434942245483,
                                                        -0.04324740916490555,
                                                        0.08499731868505478]},
                                   'IndexFinger1_L': {'Rotate': [0.07166038453578949,
                                                                 0.31002119183540344,
                                                                 -0.06010774150490761,
                                                                 0.9461176991462708]},
                                   'IndexFinger1_R': {'Rotate': [0.06960632652044296,
                                                                 0.30943235754966736,
                                                                 -0.06225083768367767,
                                                                 0.9463252425193787]},
                                   'IndexFinger2_L': {'Rotate': [-0.030458392575383186,
                                                                 0.48788759112358093,
                                                                 -0.01662372052669525,
                                                                 0.872216522693634]},
                                   'IndexFinger2_R': {'Rotate': [-0.03681386262178421,
                                                                 0.5099322199821472,
                                                                 -0.016550110653042793,
                                                                 0.8592671155929565]},
                                   'IndexFinger3_L': {'Rotate': [-0.020577354356646538,
                                                                 0.29940423369407654,
                                                                 -0.01011645793914795,
                                                                 0.9538508057594299]},
                                   'IndexFinger3_R': {'Rotate': [-0.024237021803855896,
                                                                 0.3087610900402069,
                                                                 -0.009915627539157867,
                                                                 0.9507790803909302]},
                                   'IndexFinger4_L': {'Rotate': [0.0, 0.0, 0.0, 1.0]},
                                   'IndexFinger4_R': {'Rotate': [0.0, 0.0, 0.0, 1.0]},
                                   'KneePart1_L': {'Rotate': [6.38141273157089e-06,
                                                              -1.2051271892467487e-19,
                                                              -3.110046001994168e-15,
                                                              1.0]},
                                   'KneePart1_R': {'Rotate': [6.380871127475984e-06,
                                                              -1.2487012544584522e-19,
                                                              -3.1097929509011756e-15,
                                                              1.0]},
                                   'KneePart2_L': {'Rotate': [0.0, 0.0, 0.0, 1.0]},
                                   'KneePart2_R': {'Rotate': [0.0, 0.0, 0.0, 1.0]},
                                   'Knee_L': {'Rotate': [-0.00266758119687438,
                                                         0.0009093792177736759,
                                                         0.12114177644252777,
                                                         0.9926312565803528]},
                                   'Knee_R': {'Rotate': [-0.004791453946381807,
                                                         -0.005078734830021858,
                                                         0.24885854125022888,
                                                         0.9685146808624268]},
                                   'MiddleFinger1_L': {'Rotate': [-0.026166792958974838,
                                                                  0.2752343714237213,
                                                                  -0.024426061660051346,
                                                                  0.9607105255126953]},
                                   'MiddleFinger1_R': {'Rotate': [-0.027484824880957603,
                                                                  0.2386625111103058,
                                                                  -0.02366284281015396,
                                                                  0.9704251289367676]},
                                   'MiddleFinger2_L': {'Rotate': [-0.021225688979029655,
                                                                  0.39378121495246887,
                                                                  0.0013503135414794087,
                                                                  0.9189581274986267]},
                                   'MiddleFinger2_R': {'Rotate': [-0.02383914403617382,
                                                                  0.418660968542099,
                                                                  0.0027849890757352114,
                                                                  0.9078253507614136]},
                                   'MiddleFinger3_L': {'Rotate': [-0.0042816163040697575,
                                                                  0.22482262551784515,
                                                                  0.0012571528786793351,
                                                                  0.9743894934654236]},
                                   'MiddleFinger3_R': {'Rotate': [-0.0050108470022678375,
                                                                  0.22772538661956787,
                                                                  0.001227517263032496,
                                                                  0.9737117290496826]},
                                   'MiddleFinger4_L': {'Rotate': [0.0, 0.0, 0.0, 1.0]},
                                   'MiddleFinger4_R': {'Rotate': [0.0, 0.0, 0.0, 1.0]},
                                   'Neck1_M': {'Rotate': [0.01912080869078636,
                                                          0.01736278086900711,
                                                          0.018736181780695915,
                                                          0.9994907975196838]},
                                   'Neck_M': {'Rotate': [0.013750925660133362,
                                                         -0.002844179281964898,
                                                         -0.03538094088435173,
                                                         0.999275267124176]},
                                   'PinkyFinger1_L': {'Rotate': [-0.21582727134227753,
                                                                 0.29254674911499023,
                                                                 0.07479674369096756,
                                                                 0.9285690188407898]},
                                   'PinkyFinger1_R': {'Rotate': [-0.21328048408031464,
                                                                 0.32687199115753174,
                                                                 0.07980591058731079,
                                                                 0.9172224998474121]},
                                   'PinkyFinger2_L': {'Rotate': [-0.03417103365063667,
                                                                 0.5483509302139282,
                                                                 0.07993728667497635,
                                                                 0.8317172527313232]},
                                   'PinkyFinger2_R': {'Rotate': [-0.02560468763113022,
                                                                 0.5561582446098328,
                                                                 0.07519090175628662,
                                                                 0.8272718787193298]},
                                   'PinkyFinger3_L': {'Rotate': [-0.02112036943435669,
                                                                 0.3360530734062195,
                                                                 0.048989977687597275,
                                                                 0.9403309226036072]},
                                   'PinkyFinger3_R': {'Rotate': [-0.016295431181788445,
                                                                 0.34991949796676636,
                                                                 0.04730657860636711,
                                                                 0.9354426264762878]},
                                   'PinkyFinger4_L': {'Rotate': [0.0, 0.0, 0.0, 1.0]},
                                   'PinkyFinger4_R': {'Rotate': [0.0, 0.0, 0.0, 1.0]},
                                   'RingFinger1_L': {'Rotate': [-0.09398893266916275,
                                                                0.2914368510246277,
                                                                0.05585337430238724,
                                                                0.9503215551376343]},
                                   'RingFinger1_R': {'Rotate': [-0.09679863601922989,
                                                                0.28555312752723694,
                                                                0.0520344115793705,
                                                                0.9520409107208252]},
                                   'RingFinger2_L': {'Rotate': [-0.023836994543671608,
                                                                0.4019039273262024,
                                                                0.021034803241491318,
                                                                0.9151297807693481]},
                                   'RingFinger2_R': {'Rotate': [-0.029070334509015083,
                                                                0.4257536828517914,
                                                                0.023257989436388016,
                                                                0.9040728807449341]},
                                   'RingFinger3_L': {'Rotate': [-0.009832351468503475,
                                                                0.22190117835998535,
                                                                0.011701912619173527,
                                                                0.9749493598937988]},
                                   'RingFinger3_R': {'Rotate': [-0.012058088555932045,
                                                                0.22641223669052124,
                                                                0.012321839109063148,
                                                                0.9738789796829224]},
                                   'RingFinger4_L': {'Rotate': [0.0, 0.0, 0.0, 1.0]},
                                   'RingFinger4_R': {'Rotate': [0.0, 0.0, 0.0, 1.0]},
                                   'Root_M': {'Rotate': [0.10010255128145218,
                                                         -0.028142016381025314,
                                                         -0.6605592966079712,
                                                         0.7435380220413208],
                                              'Translate': [-116.66231536865234, -102.51685333251953,
                                                            4.740273952484131]},
                                   'Scapula_L': {'Rotate': [-0.6447681784629822,
                                                            -0.0175275020301342,
                                                            0.764045000076294,
                                                            0.014211250469088554]},
                                   'Scapula_R': {'Rotate': [-0.02449636161327362,
                                                            0.658456563949585,
                                                            -0.019164595752954483,
                                                            0.7519757747650146]},
                                   'ShoulderPart1_L': {'Rotate': [0.07767314463853836,
                                                                  0.0,
                                                                  0.0,
                                                                  0.9969788789749146]},
                                   'ShoulderPart1_R': {'Rotate': [0.0791051834821701,
                                                                  0.0,
                                                                  0.0,
                                                                  0.9968662858009338]},
                                   'ShoulderPart2_L': {'Rotate': [0.07767314463853836,
                                                                  0.0,
                                                                  0.0,
                                                                  0.9969788789749146]},
                                   'ShoulderPart2_R': {'Rotate': [0.0791051834821701,
                                                                  0.0,
                                                                  0.0,
                                                                  0.9968662858009338]},
                                   'Shoulder_L': {'Rotate': [0.07318157702684402,
                                                             0.6410250067710876,
                                                             0.18964067101478577,
                                                             0.740113377571106]},
                                   'Shoulder_R': {'Rotate': [-0.07850690931081772,
                                                             0.6323488354682922,
                                                             -0.12594318389892578,
                                                             0.7603354454040527]},
                                   'Spine1_M': {'Rotate': [-0.02899857610464096,
                                                           -0.021633397787809372,
                                                           -0.04146484658122063,
                                                           0.99848473072052]},
                                   'Spine2_M': {'Rotate': [-0.040988992899656296,
                                                           -0.016581682488322258,
                                                           0.037613265216350555,
                                                           0.9983136653900146]},
                                   'Spine3_M': {'Rotate': [-0.04567251726984978,
                                                           -0.0346548892557621,
                                                           -0.06342005729675293,
                                                           0.9963387846946716]},
                                   'ThumbFinger1_L': {'Rotate': [0.6882207989692688,
                                                                 -0.28090330958366394,
                                                                 -0.3305400013923645,
                                                                 0.581540048122406]},
                                   'ThumbFinger1_R': {'Rotate': [0.6920963525772095,
                                                                 -0.2858522832393646,
                                                                 -0.32744431495666504,
                                                                 0.5762563347816467]},
                                   'ThumbFinger2_L': {'Rotate': [-0.006170950829982758,
                                                                 0.34647202491760254,
                                                                 -0.2534192204475403,
                                                                 0.9031598567962646]},
                                   'ThumbFinger2_R': {'Rotate': [-0.0038905348628759384,
                                                                 0.3411816358566284,
                                                                 -0.25528594851493835,
                                                                 0.904659628868103]},
                                   'ThumbFinger3_L': {'Rotate': [-0.017340943217277527,
                                                                 0.2974165380001068,
                                                                 -0.04152360558509827,
                                                                 0.9536867737770081]},
                                   'ThumbFinger3_R': {'Rotate': [-0.013970272615551949,
                                                                 0.30125924944877625,
                                                                 -0.04393363371491432,
                                                                 0.9524271488189697]},
                                   'ThumbFinger4_L': {'Rotate': [0.0, 0.0, 0.0, 1.0]},
                                   'ThumbFinger4_R': {'Rotate': [0.0, 0.0, 0.0, 1.0]},
                                   'ToesEnd_L': {'Rotate': [0.0, -7.534071642112394e-07, 0.0, 1.0]},
                                   'ToesEnd_R': {'Rotate': [0.0, 0.0, 0.0, 1.0]},
                                   'Toes_L': {'Rotate': [0.0017731230473145843,
                                                         -0.0020493599586188793,
                                                         -0.770032525062561,
                                                         0.6379987597465515]},
                                   'Toes_R': {'Rotate': [0.006341442931443453,
                                                         -0.007318725343793631,
                                                         -0.8135135173797607,
                                                         0.5814652442932129]},
                                   'WristEnd_L': {'Rotate': [0.0, 0.0, 0.0, 1.0]},
                                   'WristEnd_R': {'Rotate': [0.0, 0.0, 0.0, 1.0]},
                                   'Wrist_L': {'Rotate': [-0.04936154931783676,
                                                          -0.12030496448278427,
                                                          0.24146977066993713,
                                                          0.9616561532020569]},
                                   'Wrist_R': {'Rotate': [-0.07731950283050537,
                                                          -0.13055092096328735,
                                                          0.21099963784217834,
                                                          0.965638279914856]}}}
    data = pack_msg(body_msg)

    with open('body_with_head.bin', 'wb+') as f:
        f.write(data)
        print('\n压缩消息测试===========================')
        print(f'write {len(data)} bytes to body_with_head.bin ok.')


def test_decompress_by_lz4():
    test_compress_by_lz4()
    filename = r'body_with_head.bin'
    with open(filename, 'rb') as f:
        data = f.read()
        msg = MessageCompress.decompress_by_lz4(data)
        header = MessageCompress.unpack_header(data)
        print('\n解压消息测试===========================')
        print(f'read {len(data)} bytes from body_with_head.bin\n'
              f'    compressed_size: 4 + {len(data)-4} \n')

        print(f'header: {header}')


if __name__ == '__main__':
    test_decompress_by_lz4()
