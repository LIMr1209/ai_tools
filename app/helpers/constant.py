# cython: language_level=3
#  常量配置

# 上传草图生成
def intelligent_category(id=0):
    groups = [
        {"id": 1, "name": "盘子"},
        {"id": 2, "name": "杯子"},
    ]
    if id:
        for i in groups:
            if i["id"] == id:
                return i
    return groups

# 绘制草图生成
def draw_generate_category(id=0):
    groups = [
        {"id": 1, "name": "箱包"},
    ]
    if id:
        for i in groups:
            if i["id"] == id:
                return i
    return groups

# 融合发散
def fuse_divergence_category(id=0):
    groups = [
        {"id": 1, "name": "箱包"},
        {"id": 2, "name": "杯子"},
    ]
    if id:
        for i in groups:
            if i["id"] == id:
                return i
    return groups

# 图片识别标签
def get_tag():
    return [
        "MP3",
        "POS机",
        "PSP游戏机",
        "USB数据线",
        "U盘",
        "VR眼镜",
        "gps定位器",
        "usb hub",
        "万用表",
        "三脚架",
        "不锈钢椅",
        "主板",
        "交换机",
        "传真机",
        "体温计",
        "保温杯",
        "保险柜",
        "倒立机",
        "儿童座椅",
        "充电宝",
        "入耳式耳机",
        "内存条",
        "冰箱",
        "净水器",
        "    划船机",
        "刻录机光驱",
        "割草机",
        "加湿器",
        "动感单车",
        "千斤顶",
        "单肩背包",
        "卷直发器",
        "压面机",
        "双肩背包",
        "台式机主机",
        "台灯",
        "合页",
        "吊坠",
        "吊扇",
        "吊灯",
        "吸尘器",
        "吹风机",
        "呼吸机",
        "咖啡机",
        "哑铃",
        "垃圾桶",
        "壁挂炉",
        "复印机",
        "复读机",
        "多功能铁锹",
        "大力钳",
        "太阳伞",
        "头戴式耳机",
        "奖杯",
        "存储卡",
        "实木椅",
        "家用梯",
        "对讲机",
        "小太阳",
        "干鞋机",
        "平板电脑",
        "平衡车",
        "录音笔",
        "微波炉",
        "戒指",
        "手提包",
        "手机",
        "手机充电器",
        "手机支架",
        "手柄",
        "手环",
        "手电筒",
        "手表",
        "手镯手链",
        "打印机",
        "    打火机",
        "执法记录仪",
        "扫地机器人",
        "扫描枪",
        "投影仪",
        "投影幕布",
        "抽油烟机",
        "拉手",
        "挂烫机",
        "指南针",
        "指尖陀螺",
        "指甲刀",
        "按摩椅",
        "插线板",
        "搅拌机",
        "摩托车",
        "收纳盒",
        "收银机",
        "收音机",
        "放大镜",
        "断路器",
        "新风机",
        "无人机",
        "显卡",
        "智能翻译机",
        "智能锁",
        "智能马桶",
        "望远镜",
        "本册",
        "机器人",
        "机械锁",
        "概念车",
        "毛球修剪器",
        "毛笔",
        "氧气机",
        "水龙头",
        "洗牙器",
        "洗碗机",
        "洗衣机",
        "浴霸",
        "溜溜球",
        "滑板",
        "激光笔",
        "灭蚊器",
        "点验钞机",
        "烘干机",
        "烟斗",
        "烟雾报警器",
        "热水器",
        "燃气灶",
        "玉玺",
        "玻璃杯",
        "理发器",
        "电动剃须刀",
        "电动牙刷",
        "电动缝纫机",
        "电动螺丝刀",
        "电动轮椅",
        "电压力锅",
        "电子书阅读器",
        "电子烟",
        "电子秤",
        "电暖器",
        "电烙铁",
        "电烤箱",
        "电热水壶",
        "电熨斗",
        "电磁炉",
        "电脑手写板",
        "电脑电源",
        "电视",
        "电话机",
        "电饭煲",
        "电饼铛",
        "监控摄像头",
        "盘子",
        "相机",
        "眼镜",
        "砚台",
        "硒鼓",
        "硬盘",
        "碎纸机",
        "空气净化器",
        "空调",
        "笔记本散热器",
        "笔记本电脑",
        "纪念币",
        "纪念钞",
        "纸抽盒",
        "网卡",
        "网络机顶盒",
        "美工刀",
        "考勤机",
        "耳饰",
        "胎心仪",
        "臂力器",
        "自拍杆",
        "自行车",
        "节能灯",
        "花盆",
        "茶具",
        "菜刀",
        "血压计",
        "血氧仪",
        "行李箱",
        "行车记录仪",
        "装订机",
        "角磨机",
        "计算器",
        "订书机",
        "资料册",
        "足浴盆",
        "跑步机",
        "路由器",
        "车载充电器",
        "车载空气净化器",
        "转椅",
        "遥控器",
        "酒壶",
        "酒精测试仪",
        "钟表",
        "钢笔",
        "钢锯",
        "钥匙扣",
        "钱包",
        "    键盘",
        "门铃",
        "闪光灯",
        "闹钟",
        "防身刀",
        "除螨仪",
        "陶瓷杯",
        "雾化器",
        "面包机",
        "音箱",
        "音频线",
        "风扇",
        "饭盒",
        "饮水机",
        "验电笔",
        "高脚杯",
        "麦克风",
        "鼠标",
        "鼠标垫",
        "鼻毛修剪器",
    ]