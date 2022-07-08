import dataclasses

from util.types import const


class Currency:
    AED: const(str) = "AED"
    AFN: const(str) = "AFN"
    ALL: const(str) = "ALL"
    AMD: const(str) = "AMD"
    ANG: const(str) = "ANG"
    AOA: const(str) = "AOA"
    ARS: const(str) = "ARS"
    AUD: const(str) = "AUD"
    AWG: const(str) = "AWG"
    AZN: const(str) = "AZN"
    BAM: const(str) = "BAM"
    BBD: const(str) = "BBD"
    BDT: const(str) = "BDT"
    BGN: const(str) = "BGN"
    BHD: const(str) = "BHD"
    BIF: const(str) = "BIF"
    BMD: const(str) = "BMD"
    BND: const(str) = "BND"
    BOB: const(str) = "BOB"
    BRL: const(str) = "BRL"
    BSD: const(str) = "BSD"
    BTC: const(str) = "BTC"
    BTN: const(str) = "BTN"
    BWP: const(str) = "BWP"
    BYN: const(str) = "BYN"
    BYR: const(str) = "BYR"
    BZD: const(str) = "BZD"
    CAD: const(str) = "CAD"
    CDF: const(str) = "CDF"
    CHF: const(str) = "CHF"
    CLF: const(str) = "CLF"
    CLP: const(str) = "CLP"
    CNY: const(str) = "CNY"
    COP: const(str) = "COP"
    CRC: const(str) = "CRC"
    CUC: const(str) = "CUC"
    CUP: const(str) = "CUP"
    CVE: const(str) = "CVE"
    CZK: const(str) = "CZK"
    DJF: const(str) = "DJF"
    DKK: const(str) = "DKK"
    DOP: const(str) = "DOP"
    DZD: const(str) = "DZD"
    EGP: const(str) = "EGP"
    ERN: const(str) = "ERN"
    ETB: const(str) = "ETB"
    EUR: const(str) = "EUR"
    FJD: const(str) = "FJD"
    FKP: const(str) = "FKP"
    GBP: const(str) = "GBP"
    GEL: const(str) = "GEL"
    GGP: const(str) = "GGP"
    GHS: const(str) = "GHS"
    GIP: const(str) = "GIP"
    GMD: const(str) = "GMD"
    GNF: const(str) = "GNF"
    GTQ: const(str) = "GTQ"
    GYD: const(str) = "GYD"
    HKD: const(str) = "HKD"
    HNL: const(str) = "HNL"
    HRK: const(str) = "HRK"
    HTG: const(str) = "HTG"
    HUF: const(str) = "HUF"
    IDR: const(str) = "IDR"
    ILS: const(str) = "ILS"
    IMP: const(str) = "IMP"
    INR: const(str) = "INR"
    IQD: const(str) = "IQD"
    IRR: const(str) = "IRR"
    ISK: const(str) = "ISK"
    JEP: const(str) = "JEP"
    JMD: const(str) = "JMD"
    JOD: const(str) = "JOD"
    JPY: const(str) = "JPY"
    KES: const(str) = "KES"
    KGS: const(str) = "KGS"
    KHR: const(str) = "KHR"
    KMF: const(str) = "KMF"
    KPW: const(str) = "KPW"
    KRW: const(str) = "KRW"
    KWD: const(str) = "KWD"
    KYD: const(str) = "KYD"
    KZT: const(str) = "KZT"
    LAK: const(str) = "LAK"
    LBP: const(str) = "LBP"
    LKR: const(str) = "LKR"
    LRD: const(str) = "LRD"
    LSL: const(str) = "LSL"
    LTL: const(str) = "LTL"
    LVL: const(str) = "LVL"
    LYD: const(str) = "LYD"
    MAD: const(str) = "MAD"
    MDL: const(str) = "MDL"
    MGA: const(str) = "MGA"
    MKD: const(str) = "MKD"
    MMK: const(str) = "MMK"
    MNT: const(str) = "MNT"
    MOP: const(str) = "MOP"
    MRO: const(str) = "MRO"
    MUR: const(str) = "MUR"
    MVR: const(str) = "MVR"
    MWK: const(str) = "MWK"
    MXN: const(str) = "MXN"
    MYR: const(str) = "MYR"
    MZN: const(str) = "MZN"
    NAD: const(str) = "NAD"
    NGN: const(str) = "NGN"
    NIO: const(str) = "NIO"
    NOK: const(str) = "NOK"
    NPR: const(str) = "NPR"
    NZD: const(str) = "NZD"
    OMR: const(str) = "OMR"
    PAB: const(str) = "PAB"
    PEN: const(str) = "PEN"
    PGK: const(str) = "PGK"
    PHP: const(str) = "PHP"
    PKR: const(str) = "PKR"
    PLN: const(str) = "PLN"
    PYG: const(str) = "PYG"
    QAR: const(str) = "QAR"
    RON: const(str) = "RON"
    RSD: const(str) = "RSD"
    RUB: const(str) = "RUB"
    RWF: const(str) = "RWF"
    SAR: const(str) = "SAR"
    SBD: const(str) = "SBD"
    SCR: const(str) = "SCR"
    SDG: const(str) = "SDG"
    SEK: const(str) = "SEK"
    SGD: const(str) = "SGD"
    SHP: const(str) = "SHP"
    SLL: const(str) = "SLL"
    SOS: const(str) = "SOS"
    SRD: const(str) = "SRD"
    STD: const(str) = "STD"
    SVC: const(str) = "SVC"
    SYP: const(str) = "SYP"
    SZL: const(str) = "SZL"
    THB: const(str) = "THB"
    TJS: const(str) = "TJS"
    TMT: const(str) = "TMT"
    TND: const(str) = "TND"
    TOP: const(str) = "TOP"
    TRY: const(str) = "TRY"
    TTD: const(str) = "TTD"
    TWD: const(str) = "TWD"
    TZS: const(str) = "TZS"
    UAH: const(str) = "UAH"
    UGX: const(str) = "UGX"
    USD: const(str) = "USD"
    UYU: const(str) = "UYU"
    UZS: const(str) = "UZS"
    VEF: const(str) = "VEF"
    VND: const(str) = "VND"
    VUV: const(str) = "VUV"
    WST: const(str) = "WST"
    XAF: const(str) = "XAF"
    XAG: const(str) = "XAG"
    XAU: const(str) = "XAU"
    XCD: const(str) = "XCD"
    XDR: const(str) = "XDR"
    XOF: const(str) = "XOF"
    XPF: const(str) = "XPF"
    YER: const(str) = "YER"
    ZAR: const(str) = "ZAR"
    ZMK: const(str) = "ZMK"
    ZMW: const(str) = "ZMW"
    ZWL: const(str) = "ZWL"
    ALL_CURRENCIES: list[str] = [
        AED, AFN, ALL, AMD, ANG, AOA, ARS, AUD, AWG, AZN, BAM, BBD, BDT, BGN, BHD, BIF, BMD, BND, BOB, BRL, BSD, BTC,
        BTN, BWP, BYN, BYR, BZD, CAD, CDF, CHF, CLF, CLP, CNY, COP, CRC, CUC, CUP, CVE, CZK, DJF, DKK, DOP, DZD, EGP,
        ERN, ETB, EUR, FJD, FKP, GBP, GEL, GGP, GHS, GIP, GMD, GNF, GTQ, GYD, HKD, HNL, HRK, HTG, HUF, IDR, ILS, IMP,
        INR, IQD, IRR, ISK, JEP, JMD, JOD, JPY, KES, KGS, KHR, KMF, KPW, KRW, KWD, KYD, KZT, LAK, LBP, LKR, LRD, LSL,
        LTL, LVL, LYD, MAD, MDL, MGA, MKD, MMK, MNT, MOP, MRO, MUR, MVR, MWK, MXN, MYR, MZN, NAD, NGN, NIO, NOK, NPR,
        NZD, OMR, PAB, PEN, PGK, PHP, PKR, PLN, PYG, QAR, RON, RSD, RUB, RWF, SAR, SBD, SCR, SDG, SEK, SGD, SHP, SLL,
        SOS, SRD, STD, SVC, SYP, SZL, THB, TJS, TMT, TND, TOP, TRY, TTD, TWD, TZS, UAH, UGX, USD, UYU, UZS, VEF, VND,
        VUV, WST, XAF, XAG, XAU, XCD, XDR, XOF, XPF, YER, ZAR, ZMK, ZMW, ZWL
    ]

@dataclasses.dataclass
class Money:
    amount: float
    currency: str = Currency.EUR

    def __eq__(self, other: 'Money') -> bool:
        ...
