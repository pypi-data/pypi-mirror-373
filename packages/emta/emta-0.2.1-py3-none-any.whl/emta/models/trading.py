"""Data models for trading operations."""

from dataclasses import dataclass, field, fields
from decimal import Decimal
from enum import Enum
from typing import TypedDict


@dataclass
class AccountOverview:
    """账户资金总览数据类"""

    Djzj: float  # 冻结资金
    Dryk: float  # 当日盈亏
    Kqzj: float  # 可取资金
    Kyzj: float  # 可用资金
    Ljyk: float  # 累计盈亏
    Money_type: str  # 货币类型
    RMBZzc: float  # 人民币总资产
    Zjye: float  # 资金余额
    Zxsz: float  # 证券市值
    Zzc: float  # 总资产

    def __post_init__(self) -> None:
        # 确保所有数值字段都是浮点数
        for v in fields(self):
            if v.name not in ["Money_type"]:
                value = getattr(self, v.name)
                if isinstance(value, str):
                    setattr(self, v.name, float(value))

    def __str__(self) -> str:
        """格式化打印账户信息"""
        title = "账户资金总览"
        separator = "=" * 50

        # 创建格式化字符串
        lines = [
            separator,
            f"{title:^50}",
            separator,
            f"{'货币类型:':<20} {self.Money_type:>30}",
            f"{'总资产： ':<20} {self.Zzc:>30,.2f}",
            f"{'证券市值:':<20} {self.Zxsz:>30,.2f}",
            f"{'可用资金:':<20} {self.Kyzj:>30,.2f}",
            f"{'可取资金:':<20} {self.Kqzj:>30,.2f}",
            f"{'冻结资金:':<20} {self.Djzj:>30,.2f}",
            f"{'累计盈亏:':<20} {self.Ljyk:>30,.2f}",
            f"{'当日盈亏:':<20} {self.Dryk:>30,.2f}",
            f"{'资金余额:':<20} {self.Zjye:>30,.2f}",
            separator,
        ]

        return "\n".join(lines)


@dataclass
class Position:
    """持仓明细数据类"""

    Bz: str  # 币种
    Cbjg: Decimal  # 成本价格
    Cbjgex: Decimal  # 成本价格(精确)
    Ckcb: Decimal  # 持仓成本
    Ckcbj: Decimal  # 持仓成本价
    Ckyk: Decimal  # 持仓盈亏
    Cwbl: Decimal  # 仓位比例
    Djsl: int  # 冻结数量
    Dqcb: Decimal  # 当前成本
    Dryk: Decimal  # 当日盈亏
    Drykbl: Decimal  # 当日盈亏比例
    Gddm: str  # 股东代码
    Gfmcdj: int  # 股份卖出冻结
    Gfmrjd: int  # 股份买入解冻
    Gfssmmce: int  # 股份上市末码额
    Gfye: int  # 股份余额
    Jgbm: str  # 机构编码
    Khdm: str  # 客户代码
    Ksssl: int  # 可售数量
    Kysl: int  # 可用数量
    Ljyk: Decimal  # 累计盈亏
    Market: str  # 市场
    Mrssc: int  # 买入市场
    Sssl: int  # 申购数量
    Szjsbs: int  # 市值计算标识
    Ykbl: Decimal  # 盈亏比例
    Zjzh: str  # 资金账号
    Zqdm: str  # 证券代码
    Zqlx: str  # 证券类型
    Zqlxmc: str  # 证券类型名称
    Zqmc: str  # 证券名称
    Zqsl: int  # 证券数量
    Ztmc: int  # 状态码
    Ztmr: int  # 状态码
    Zxjg: Decimal  # 最新价格
    Zxsz: Decimal  # 最新市值
    zqzwqc: str  # 证券中文全称
    zxsznew: Decimal  # 最新市值(新)

    def __post_init__(self) -> None:
        # 转换数值类型
        decimal_fields = [
            "Cbjg",
            "Cbjgex",
            "Ckcb",
            "Ckcbj",
            "Ckyk",
            "Cwbl",
            "Dqcb",
            "Dryk",
            "Drykbl",
            "Ljyk",
            "Ykbl",
            "Zxjg",
            "Zxsz",
            "zxsznew",
        ]

        int_fields = [
            "Djsl",
            "Gfmcdj",
            "Gfmrjd",
            "Gfssmmce",
            "Gfye",
            "Ksssl",
            "Kysl",
            "Mrssc",
            "Sssl",
            "Szjsbs",
            "Zqsl",
            "Ztmc",
            "Ztmr",
        ]

        for field_name in decimal_fields:
            value = getattr(self, field_name)
            if isinstance(value, str):
                setattr(self, field_name, Decimal(value))

        for field_name in int_fields:
            value = getattr(self, field_name)
            if isinstance(value, str):
                setattr(self, field_name, int(value))


@dataclass
class Portfolio:
    """持仓组合数据类，包含多个持仓"""

    positions: list[Position] = field(default_factory=list)

    def add_position(self, position: Position) -> None:
        """添加持仓"""
        self.positions.append(position)

    def __str__(self) -> str:
        """格式化打印持仓信息"""
        if not self.positions:
            return "暂无持仓"

        # 表头 - 使用固定宽度确保对齐
        headers = [
            "证券名称",
            "证券代码",
            "当前价",
            "持仓数量",
            "成本价",
            "当前市值",
            "累计盈亏",
            "盈亏比例",
        ]
        col_widths = [12, 10, 10, 12, 10, 12, 12, 12]  # 每列宽度

        # 构建表头
        header_line = "".join(
            f"{header:<{width}}"
            for header, width in zip(headers, col_widths, strict=False)
        )
        separator = "-" * sum(col_widths)

        # 构建表格行
        rows = [header_line, separator]
        total_market_value = Decimal("0")
        total_profit_loss = Decimal("0")

        for pos in self.positions:
            # 格式化数据
            name = pos.Zqmc if len(pos.Zqmc) <= 10 else pos.Zqmc[:7] + "..."
            code = pos.Zqdm
            price = f"{pos.Zxjg:.3f}"
            quantity = f"{pos.Zqsl:,}"
            cost = f"{pos.Cbjg:.3f}"
            market_value = f"{pos.Zxsz:,.2f}"
            profit_loss = f"{pos.Ljyk:,.2f}"
            profit_ratio = f"{pos.Ykbl:.2%}"

            # 构建行
            row_data = [
                name,
                code,
                price,
                quantity,
                cost,
                market_value,
                profit_loss,
                profit_ratio,
            ]
            row = "".join(
                f"{data:<{width}}"
                for data, width in zip(row_data, col_widths, strict=False)
            )
            rows.append(row)

            # 累加总市值和总盈亏
            total_market_value += pos.Zxsz
            total_profit_loss += pos.Ljyk

        # 添加总计行
        rows.append(separator)
        total_row_data = [
            "总计",
            "",
            "",
            "",
            "",
            f"{total_market_value:,.2f}",
            f"{total_profit_loss:,.2f}",
            "",
        ]
        total_row = "".join(
            f"{data:<{width}}"
            for data, width in zip(total_row_data, col_widths, strict=False)
        )
        rows.append(total_row)

        return "\n".join(rows)


class OrderType(Enum):
    """Order types for trading"""

    BUY = "B"
    SELL = "S"


class OrderStatus(Enum):
    """Order status types"""

    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


@dataclass
class Order:
    """Represents a trading order"""

    symbol: str
    order_type: OrderType
    quantity: float
    price: float
    order_id: str | None = None
    status: OrderStatus = OrderStatus.PENDING


class AccountInfo(TypedDict):
    """Represents account information"""

    username: str
    account_overview: AccountOverview
    portfolio: Portfolio


class MarketData(TypedDict):
    """Represents market data for a symbol"""

    symbol: str
    last_price: float
    bid_price: float
    ask_price: float
    volume: int
    timestamp: str


# 使用示例
if __name__ == "__main__":
    # 从JSON数据创建对象
    json_data: dict[str, object] = {
        "Status": 0,
        "Count": 0,
        "Data": [
            {
                "Djzj": "0.00",
                "Dryk": "0.00",
                "Kqzj": "447.26",
                "Kyzj": "452.23",
                "Ljyk": "-1540.00",
                "Money_type": "RMB",
                "RMBZzc": "152788.23",
                "Zjye": "447.26",
                "Zxsz": "152340.97",
                "Zzc": "152788.23",
            }
        ],
        "Errcode": 0,
    }

    # 提取Data中的第一个元素
    data = json_data["Data"][0]  # type: ignore

    # 创建AccountOverview实例
    account = AccountOverview(
        Djzj=data["Djzj"],
        Dryk=data["Dryk"],
        Kqzj=data["Kqzj"],
        Kyzj=data["Kyzj"],
        Ljyk=data["Ljyk"],
        Money_type=data["Money_type"],
        RMBZzc=data["RMBZzc"],
        Zjye=data["Zjye"],
        Zxsz=data["Zxsz"],
        Zzc=data["Zzc"],
    )

    # 打印格式化后的账户信息
    print(account)

    # 从JSON数据创建持仓对象
    json_data_positions: dict[str, object] = {
        "Status": 0,
        "Count": 0,
        "Data": [
            {
                "positions": [
                    {
                        "Bz": "RMB",
                        "Cbjg": "1.000",
                        "Cbjgex": "1.000",
                        "Ckcb": "2000.00",
                        "Ckcbj": "1.000",
                        "Ckyk": "-1540.00",
                        "Cwbl": "0.00301",
                        "Djsl": "0",
                        "Dqcb": "2000.00",
                        "Dryk": "0.00",
                        "Drykbl": "0.000000",
                        "Gddm": "0235371788",
                        "Gfmcdj": "0",
                        "Gfmrjd": "0",
                        "Gfssmmce": "0",
                        "Gfye": "2000",
                        "Jgbm": "5408",
                        "Khdm": "540860219538",
                        "Ksssl": "2000",
                        "Kysl": "2000",
                        "Ljyk": "-1540.00",
                        "Market": "TA",
                        "Mrssc": "0",
                        "Sssl": "0",
                        "Szjsbs": "1",
                        "Ykbl": "-0.770000",
                        "Zjzh": "540868886633",
                        "Zqdm": "400251",
                        "Zqlx": "0",
                        "Zqlxmc": "0",
                        "Zqmc": "海印5",
                        "Zqsl": "2000",
                        "Ztmc": "0",
                        "Ztmr": "0",
                        "Zxjg": "0.230",
                        "Zxsz": "460.00",
                        "zqzwqc": "海印5",
                        "zxsznew": "460.00",
                    },
                    {
                        "Bz": "RMB",
                        "Cbjg": "8.830",
                        "Cbjgex": "8.830",
                        "Ckcb": "151876.00",
                        "Ckcbj": "8.830",
                        "Ckyk": "0.00",
                        "Cwbl": "0.99403",
                        "Djsl": "0",
                        "Dqcb": "151876.00",
                        "Dryk": "0.00",
                        "Drykbl": "0.000000",
                        "Gddm": "0235371788",
                        "Gfmcdj": "0",
                        "Gfmrjd": "0",
                        "Gfssmmce": "0",
                        "Gfye": "17200",
                        "Jgbm": "5408",
                        "Khdm": "540860219538",
                        "Ksssl": "17200",
                        "Kysl": "17200",
                        "Ljyk": "0.00",
                        "Market": "B",
                        "Mrssc": "0",
                        "Sssl": "0",
                        "Szjsbs": "1",
                        "Ykbl": "0.000000",
                        "Zjzh": "540868886633",
                        "Zqdm": "920100",
                        "Zqlx": "J",
                        "Zqlxmc": "J",
                        "Zqmc": "三协电机",
                        "Zqsl": "17200",
                        "Ztmc": "0",
                        "Ztmr": "0",
                        "Zxjg": "8.830",
                        "Zxsz": "151876.00",
                        "zqzwqc": "三协电机",
                        "zxsznew": "151876.00",
                    },
                ]
            }
        ],
        "Errcode": 0,
    }

    # 创建持仓组合
    portfolio = Portfolio()

    # 提取并添加所有持仓
    for pos_data in json_data_positions["Data"][0]["positions"]:  # type: ignore
        position = Position(**pos_data)
        portfolio.add_position(position)

    print(portfolio)
