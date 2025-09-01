# -*- coding: utf-8 -*-
"""
城市名称到机场代码映射字典
格式：{"城市名(机场代码)": "机场代码小写"}
"""

CITIES_DICT = {
    "上海(SHA)": "sha",
    "北京(BJS)": "bjs",
    "成都(CTU)": "ctu",
    "广州(CAN)": "can",
    "乌鲁木齐(URC)": "urc",
    "昆明(KMG)": "kmg",
    "深圳(SZX)": "szx",
    "重庆(CKG)": "ckg",
    "西安(SIA)": "sia",
    "杭州(HGH)": "hgh",
    "青岛(TAO)": "tao",
    "三亚(SYX)": "syx",
    "南京(NKG)": "nkg",
    "哈尔滨(HRB)": "hrb",
    "贵阳(KWE)": "kwe",
    "大连(DLC)": "dlc",
    "长沙(CSX)": "csx",
    "沈阳(SHE)": "she",
    "厦门(XMN)": "xmn",
    "海口(HAK)": "hak",
    "中国澳门(MFM)": "mfm",
    "阿里(NGQ)": "ngq",
    "安康(AKA)": "aka",
    "阿克苏(AKU)": "aku",
    "阿勒泰(AAT)": "aat",
    "安庆(AQG)": "aqg",
    "鞍山(AOG)": "aog",
    "安顺(AVA)": "ava",
    "安阳(AYN)": "ayn",
    "阿尔山(YIE)": "yie",
    "阿拉尔(ACF)": "acf",
    "阿拉善左旗(AXF)": "axf",
    "阿拉善右旗(RHT)": "rht",
    "包头(BAV)": "bav",
    "北海(BHY)": "bhy",
    "保山(BSD)": "bsd",
    "白山(NBS)": "nbs",
    "白城(DBC)": "dbc",
    "百色(AEB)": "aeb",
    "博乐(BPL)": "bpl",
    "布尔津(KJI)": "kji",
    "巴彦淖尔(RLK)": "rlk",
    "巴中(BZX)": "bzx",
    "巴里坤(DHH)": "dhh",
    "毕节(BFJ)": "bfj",
    "长治(CIH)": "cih",
    "长春(CGQ)": "cgq",
    "常德(CGD)": "cgd",
    "赤峰(CIF)": "cif",
    "朝阳(CHG)": "chg",
    "常州(CZX)": "czx",
    "池州(JUH)": "juh",
    "承德(CDE)": "cde",
    "昌都(BPX)": "bpx",
    "郴州(HCZ)": "hcz",
    "沧源(CWJ)": "cwj",
    "敦煌(DNH)": "dnh",
    "大理(DLU)": "dlu",
    "迪庆(DIG)": "dig",
    "大同(DAT)": "dat",
    "丹东(DDG)": "ddg",
    "大庆(DQA)": "dqa",
    "东营(DOY)": "doy",
    "稻城(DCY)": "dcy",
    "达州(DZH)": "dzh",
    "德令哈(HXD)": "hxd",
    "恩施(ENH)": "enh",
    "鄂州(EHU)": "ehu",
    "鄂尔多斯(DSN)": "dsn",
    "额济纳旗(EJN)": "ejn",
    "二连浩特(ERL)": "erl",
    "佛山(FUO)": "fuo",
    "富蕴(FYN)": "fyn",
    "阜阳(FUG)": "fug",
    "福州(FOC)": "foc",
    "抚远(FYJ)": "fyj",
    "桂林(KWL)": "kwl",
    "格尔木(GOQ)": "goq",
    "广元(GYS)": "gys",
    "赣州(KOW)": "kow",
    "固原(GYU)": "gyu",
    "中国高雄(KHH)": "khh",
    "甘孜(GZG)": "gzg",
    "果洛(GMQ)": "gmq",
    "黄山(TXN)": "txn",
    "呼和浩特(HET)": "het",
    "汉中(HZG)": "hzg",
    "海拉尔(HLD)": "hld",
    "邯郸(HDG)": "hdg",
    "合肥(HFE)": "hfe",
    "黑河(HEK)": "hek",
    "怀化(HJJ)": "hjj",
    "哈密(HMI)": "hmi",
    "和田(HTN)": "htn",
    "衡阳(HNY)": "hny",
    "惠州(HUZ)": "huz",
    "淮安(HIA)": "hia",
    "菏泽(HZA)": "hza",
    "花土沟(HTT)": "htt",
    "和静(HJB)": "hjb",
    "河池(HCJ)": "hcj",
    "霍林郭勒(HUO)": "huo",
    "中国花莲(HUN)": "hun",
    "红原(AHJ)": "ahj",
    "九江(JIU)": "jiu",
    "九寨沟(JZH)": "jzh",
    "济南(TNA)": "tna",
    "鸡西(JXA)": "jxa",
    "景德镇(JDZ)": "jdz",
    "井冈山(JGS)": "jgs",
    "佳木斯(JMU)": "jmu",
    "济宁(JNG)": "jng",
    "嘉峪关(JGN)": "jgn",
    "锦州(JNZ)": "jnz",
    "荆州(SHS)": "shs",
    "揭阳(SWA)": "swa",
    "加格达奇(JGD)": "jgd",
    "金昌(JIC)": "jic",
    "建三江(JSJ)": "jsj",
    "中国嘉义(CYI)": "cyi",
    "中国金门(KNH)": "knh",
    "泉州（晋江）(JJN)": "jjn",
    "喀什(KHG)": "khg",
    "克拉玛依(KRY)": "kry",
    "库车(KCA)": "kca",
    "库尔勒(KRL)": "krl",
    "凯里(KJH)": "kjh",
    "康定(KGT)": "kgt",
    "丽江(LJG)": "ljg",
    "拉萨(LXA)": "lxa",
    "兰州(LHW)": "lhw",
    "林芝(LZY)": "lzy",
    "临汾(LFQ)": "lfq",
    "丽水(LIJ)": "lij",
    "龙岩(LCX)": "lcx",
    "洛阳(LYA)": "lya",
    "连云港(LYG)": "lyg",
    "柳州(LZH)": "lzh",
    "泸州(LZO)": "lzo",
    "临沂(LYI)": "lyi",
    "六盘水(LPF)": "lpf",
    "临沧(LNJ)": "lnj",
    "荔波(LLB)": "llb",
    "阆中(LZG)": "lzg",
    "黎平(HZH)": "hzh",
    "澜沧(JMJ)": "jmj",
    "吕梁(LLV)": "llv",
    "陇南(LNL)": "lnl",
    "龙岩（连城）(LCX)": "lcx",
    "牡丹江(MDG)": "mdg",
    "漠河(OHE)": "ohe",
    "绵阳(MIG)": "mig",
    "满洲里(NZH)": "nzh",
    "茅台(WMT)": "wmt",
    "梅州(MXZ)": "mxz",
    "芒市(LUM)": "lum",
    "中国马公(MZG)": "mzg",
    "中国马祖(MFK)": "mfk",
    "南通(NTG)": "ntg",
    "宁波(NGB)": "ngb",
    "南昌(KHN)": "khn",
    "南充(NAO)": "nao",
    "南宁(NNG)": "nng",
    "南阳(NNY)": "nny",
    "宁蒗(NLH)": "nlh",
    "中国南竿(LZN)": "lzn",
    "攀枝花(PZI)": "pzi",
    "普洱(SYM)": "sym",
    "普兰(APJ)": "apj",
    "琼海(BAR)": "bar",
    "秦皇岛(BPE)": "bpe",
    "齐齐哈尔(NDG)": "ndg",
    "且末(IQM)": "iqm",
    "庆阳(IQN)": "iqn",
    "泉州(JJN)": "jjn",
    "衢州(JUZ)": "juz",
    "祁连(HBQ)": "hbq",
    "奇台(JBK)": "jbk",
    "黔江(JIQ)": "jiq",
    "日喀则(RKZ)": "rkz",
    "日照(RIZ)": "riz",
    "若羌(RQA)": "rqa",
    "上饶(SQD)": "sqd",
    "绥芬河(HSF)": "hsf",
    "韶关(HSC)": "hsc",
    "石河子(SHF)": "shf",
    "石家庄(SJW)": "sjw",
    "三明(SQJ)": "sqj",
    "山南(LGZ)": "lgz",
    "十堰(WDS)": "wds",
    "神农架(HPG)": "hpg",
    "邵阳(WGN)": "wgn",
    "松原(YSQ)": "ysq",
    "朔州(SZH)": "szh",
    "三沙(XYI)": "xyi",
    "莎车(QSZ)": "qsz",
    "泉州（石狮）(JJN)": "jjn",
    "揭阳（汕头）(SWA)": "swa",
    "天津(TSN)": "tsn",
    "太原(TYN)": "tyn",
    "塔城(TCG)": "tcg",
    "通化(TNH)": "tnh",
    "通辽(TGO)": "tgo",
    "天水(THQ)": "thq",
    "唐山(TVS)": "tvs",
    "台州(HYN)": "hyn",
    "中国台北(TPE)": "tpe",
    "铜仁(TEN)": "ten",
    "腾冲(TCZ)": "tcz",
    "中国台南(TNN)": "tnn",
    "中国台东(TTT)": "ttt",
    "中国台中(RMQ)": "rmq",
    "塔什库尔干(HQL)": "hql",
    "吐鲁番(TLQ)": "tlq",
    "图木舒克(TWC)": "twc",
    "扬州（泰州）(YTY)": "yty",
    "无锡(WUX)": "wux",
    "武夷山(WUS)": "wus",
    "五大连池(DTU)": "dtu",
    "潍坊(WEF)": "wef",
    "武汉(WUH)": "wuh",
    "芜湖(WHU)": "whu",
    "威海(WEH)": "weh",
    "乌兰浩特(HLH)": "hlh",
    "万州(WXN)": "wxn",
    "温州(WNZ)": "wnz",
    "梧州(WUZ)": "wuz",
    "乌海(WUA)": "wua",
    "文山(WNH)": "wnh",
    "乌拉特中旗(WZQ)": "wzq",
    "武隆(CQW)": "cqw",
    "巫山(WSK)": "wsk",
    "乌兰察布(UCB)": "ucb",
    "西双版纳(JHG)": "jhg",
    "中国香港(HKG)": "hkg",
    "西宁(XNN)": "xnn",
    "西昌(XIC)": "xic",
    "襄阳(XFN)": "xfn",
    "夏河(GXH)": "gxh",
    "锡林浩特(XIL)": "xil",
    "信阳(XAI)": "xai",
    "徐州(XUZ)": "xuz",
    "忻州(WUT)": "wut",
    "邢台(XNT)": "xnt",
    "兴义(ACX)": "acx",
    "新源(NLT)": "nlt",
    "湘西土家族苗族自治州(DXJ)": "dxj",
    "西安（咸阳）(SIA)": "sia",
    "迪庆（香格里拉）(DIG)": "dig",
    "扬州(YTY)": "yty",
    "银川(INC)": "inc",
    "延安(ENY)": "eny",
    "运城(YCU)": "ycu",
    "宜宾(YBP)": "ybp",
    "宜昌(YIH)": "yih",
    "伊春(LDS)": "lds",
    "宜春(YIC)": "yic",
    "延吉(YNJ)": "ynj",
    "榆林(UYN)": "uyn",
    "伊宁(YIN)": "yin",
    "烟台(YNT)": "ynt",
    "义乌(YIW)": "yiw",
    "岳阳(YYA)": "yya",
    "永州(LLF)": "llf",
    "玉林(YLX)": "ylx",
    "盐城(YNZ)": "ynz",
    "营口(YKH)": "ykh",
    "于田(YTW)": "ytw",
    "玉树(YUS)": "yus",
    "舟山(HSN)": "hsn",
    "张家界(DYG)": "dyg",
    "珠海(ZUH)": "zuh",
    "湛江(ZHA)": "zha",
    "张家口(ZQZ)": "zqz",
    "昭通(ZAT)": "zat",
    "中卫(ZHY)": "zhy",
    "遵义(ZYI)": "zyi",
    "郑州(CGO)": "cgo",
    "张掖(YZY)": "yzy",
    "扎兰屯(NZL)": "nzl",
    "昭苏(ZFL)": "zfl",
    "怀化（芷江）(HJJ)": "hjj"
}

# 反向映射字典：机场代码(小写) -> 完整城市名
AIRPORT_TO_CITY = {v: k for k, v in CITIES_DICT.items()}

# 城市名到机场代码映射（不包含括号）
CITY_NAME_TO_CODE = {
    key.split('(')[0]: value for key, value in CITIES_DICT.items()
}

def get_airport_code(city_input):
    """
    根据输入获取机场代码(小写)
    支持多种输入格式：
    - 完整格式：上海(SHA)
    - 城市名：上海
    - 机场代码：SHA、sha
    """
    city_input = city_input.strip()
    
    # 直接匹配完整格式
    if city_input in CITIES_DICT:
        return CITIES_DICT[city_input]
    
    # 匹配城市名
    if city_input in CITY_NAME_TO_CODE:
        return CITY_NAME_TO_CODE[city_input]
    
    # 匹配机场代码（转换为小写）
    code_lower = city_input.lower()
    if code_lower in AIRPORT_TO_CITY:
        return code_lower
    
    return None

def get_city_name(city_input):
    """
    根据输入获取完整城市名
    """
    city_input = city_input.strip()
    
    # 直接匹配完整格式
    if city_input in CITIES_DICT:
        return city_input
    
    # 匹配城市名
    if city_input in CITY_NAME_TO_CODE:
        for full_name in CITIES_DICT.keys():
            if full_name.startswith(city_input + '('):
                return full_name
    
    # 匹配机场代码
    code_lower = city_input.lower()
    if code_lower in AIRPORT_TO_CITY:
        return AIRPORT_TO_CITY[code_lower]
    
    return None

if __name__ == "__main__":
    # 测试示例
    test_inputs = ["上海(SHA)", "上海", "SHA", "sha", "北京", "BJS"]
    
    print("测试城市字典功能：")
    for test_input in test_inputs:
        airport_code = get_airport_code(test_input)
        city_name = get_city_name(test_input)
        print(f"输入: {test_input} -> 机场代码: {airport_code}, 城市全名: {city_name}")
    
    print(f"\n总共支持 {len(CITIES_DICT)} 个城市") 