# %%
import numpy as np
import pandas as pd
from .draw import draw


class ExchangeBase:
    def __init__(self, initial_balance=10000, recorded=False):
        self.initial_balance = initial_balance  # 初始的资产
        self.recorded = recorded  # 是否记录历史
        self.opt = {
            'trades': [],
            'history': []  # 集成 history 到 opt 中
        }
        self.account = {'USDT': {'realised_profit': 0, 'unrealised_profit': 0, 'total': initial_balance,
                                 'fee': 0, 'leverage': 0, 'hold': 0, 'long': 0, 'short': 0}}

    def record_history(self, time):
        """记录当前总资产和时间到 history 中"""
        self.opt['history'].append({
            'date': time,
            'total': self.account['USDT']['total']
        })
    
    def __getitem__(self, symbol):
        return self.account.get(symbol, None)
    
    def __setitem__(self, symbol, value):
        self.account[symbol] = value

    @property
    def activate_symbols(self):
        return [symbol for symbol in self.trade_symbols if self.account[symbol]['amount'] != 0]

    @property
    def total(self):
        return self.account['USDT']['total']

    @property
    def leverage(self):
        return self.account['USDT']['leverage']

    @property
    def realised_profit(self):
        return self.account['USDT']['realised_profit']

    @property
    def unrealised_profit(self):
        return self.account['USDT']['unrealised_profit']

    @property
    def history(self):
        if not self.recorded:
            raise ValueError("History is only available in recorded mode.")
        return self.opt['history']
    
    @property
    def available_margin(self):
        return self.account['USDT']['total'] - self.account['USDT']['hold']

    @property
    def realised_profit(self):
        return self.account['USDT']['realised_profit']

    @property
    def trades(self):
        return self.opt['trades']

    @property
    def stats(self):
        if not self.recorded:
            raise ValueError("Stats are only available in recorded mode.")

        if not self.opt['history']:
            return {
                '初始资产': f'{self.initial_balance:.2f} USDT',
                '当前资产': f'{self.account["USDT"]["total"]:.2f} USDT',
                '已实现利润': f'{self.account["USDT"]["realised_profit"]:.2f} USDT',
                '未实现利润': f'{self.account["USDT"]["unrealised_profit"]:.2f} USDT',
                '总手续费': f'{self.account["USDT"]["fee"]:.2f} USDT',
                '杯杆率': f'{self.account["USDT"]["leverage"]:.2f}',
                '活跃交易对数量': len(self.activate_symbols),
                '持仓价值': f'{self.account["USDT"]["hold"]:.2f} USDT',
                '多头持仓价值': f'{self.account["USDT"]["long"]:.2f} USDT',
                '空头持仓价值': f'{self.account["USDT"]["short"]:.2f} USDT',
                '总交易笔数': 0,
                '胜率': '0.00%',
                '年化收益率': '0.00%',
                '最大回撤时间范围': 'N/A',
                '最大回撤': '0.00%',
                '夏普比率': '0.00'
            }

        # 创建一个账户历史的DataFrame
        history_df = pd.DataFrame(self.opt['history'])
        history_df = history_df.sort_values(by='date')
        history_df = history_df.drop_duplicates(subset='date')
        history_df = history_df.set_index('date')

        # 计算累计收益
        history_df['max2here'] = history_df['total'].expanding().max()
        history_df['dd2here'] = history_df['total'] / history_df['max2here'] - 1
        drwa_down_df = history_df.sort_values(by=['dd2here'])
        drwa_down_df = drwa_down_df[drwa_down_df['dd2here'] < 0]
        if drwa_down_df.empty:
            start_date = np.nan
            end_data = np.nan
            max_draw_down = 0
        else:
            max_draw_down = drwa_down_df.iloc[0]['dd2here']
            end_data = drwa_down_df.iloc[0].name
            start_date = history_df[history_df.index <= end_data].sort_values(by='total', ascending=False).iloc[0].name

        # 计算胜率
        total_trades = len(self.opt['trades'])
        if total_trades == 0:
            win_rate = 0
        else:
            winning_trades = sum(1 for trade in self.opt['trades'] if trade['pos'] > 0)
            losing_trades = sum(1 for trade in self.opt['trades'] if trade['pos'] < 0)
            win_rate = winning_trades / (winning_trades + losing_trades) if (winning_trades + losing_trades) > 0 else 0

        # 计算年化收益率
        if len(history_df) < 2:
            annual_return = 0
        else:
            start_date_for_return = history_df.index[0]
            end_date_for_return = history_df.index[-1]
            total_days = (end_date_for_return - start_date_for_return).days
            if total_days > 0:
                annual_return = ((history_df['total'].iloc[-1] / self.initial_balance) ** (365 / total_days) - 1)
            else:
                annual_return = 0

        # 计算夏普比率
        # 计算每日收益率
        daily_history = history_df['total'].resample('D').ffill().dropna()
        daily_returns = daily_history.pct_change().dropna()
        if len(daily_returns) > 1:
            risk_free_rate = 0.03 / 365
            sharpe_ratio = (daily_returns.mean() - risk_free_rate) / daily_returns.std() * np.sqrt(365)
        else:
            sharpe_ratio = 0

        stats = {
            '初始资产': f'{self.initial_balance:.2f} USDT',
            '当前资产': f'{self.account["USDT"]["total"]:.2f} USDT',
            '已实现利润': f'{self.account["USDT"]["realised_profit"]:.2f} USDT',
            '未实现利润': f'{self.account["USDT"]["unrealised_profit"]:.2f} USDT',
            '总手续费': f'{self.account["USDT"]["fee"]:.2f} USDT',
            '活跃交易对数量': len(self.activate_symbols),
            '持仓价值': f'{self.account["USDT"]["hold"]:.2f} USDT',
            '多头持仓价值': f'{self.account["USDT"]["long"]:.2f} USDT',
            '空头持仓价值': f'{self.account["USDT"]["short"]:.2f} USDT',
            '总交易笔数': total_trades,
            '胜率': f'{win_rate:.2%}',
            '年化收益率': f'{annual_return:.2%}',
            '最大回撤时间范围': (start_date,end_data),
            '最大回撤': f'{max_draw_down:.2%}',
            '夏普比率': f'{sharpe_ratio:.2f}'
        }
        return stats

    def draw(self, data_df: pd.DataFrame, title: str, indicators: list, show_kline=True, show_total=True, show_base=False):
        """
        :param data_df: 数据 DataFrame
        :param title: 图表标题
        :param indicators: 画图指标 [[('指标名', '指标类型'), ('指标名', '指标类型')], [('指标名', '指标类型')]]
        :param show_kline: 是否显示K线图
        :param show_total: 是否显示总资产曲线
        """

        # 将 self.history 转换为 DataFrame
        history_df = pd.DataFrame(self.opt['history'])

        # 按照 'date' 分组，并保留每组的最后一条记录
        history_df = history_df.sort_values('date').groupby('date', as_index=False).last()

        # 按照 'date' 将 history_df 和 data_df 合并
        data_df = pd.merge(data_df, history_df, on='date', how='left')

        # 使用前向填充处理 'total' 列的缺失值
        data_df['total'] = data_df['total'].ffill()

        data_dict = []
        if show_kline:
            # 如果signal列存在，将signal列的值赋值给signal列
            opt = {
                "series_name": "K",
                "draw_type": "Kline",
                "col": ["open", "close", "low", "high"],
                "height": 50,
            }
            if 'signal' in data_df.columns:
                opt['trade_single'] = 'signal'
            data_dict.append(opt)


        if indicators:
            for ind in indicators:
                ind_data = {}
                for i, indicator in enumerate(ind):
                    if i == 0:
                        ind_data = {
                            "series_name": indicator[0],
                            "draw_type": indicator[1],
                            "height": 0,
                        }
                    else:
                        if 'sub_chart' not in ind_data:
                            ind_data['sub_chart'] = []
                        ind_data['sub_chart'].append(
                            {"series_name": indicator[0], "draw_type": indicator[1]}
                        )
                data_dict.append(ind_data)
        
        if show_total:
            # 绘制基准收益曲线
            total_dict = {
                "series_name": "total",
                "draw_type": "Line",
                "height": 0,
            }
            if show_base:
                data_df.loc[:, "base"] = (data_df["close"] / data_df["close"].iloc[0]) * self.initial_balance
                total_dict['sub_chart'] = [
                    {"series_name": "base", "draw_type": "Line"},
                ]
            data_dict.append(total_dict)
            

        sub_width = 40 / (len(data_dict) - 1)
        for d in data_dict:
            if d['draw_type'] != "Kline":
                d['height'] = sub_width

        draw(   
            data_df,
            data_dict=data_dict,
            date_col="date",
            date_formate="%Y-%m-%d %H:%M:%S",
            title=title,
            height_type="%",
            auto_play_space="""
                function auto_play_space(xi){
                    return 200;
            }""",
            show=True,
            display_js="""
            // 设置 dataZoom 为最大范围
            window.onload = function() {
                var isSettingZoom = false;

                // 获取 x 轴的数据
                var xData = chart_option.xAxis[0].data;
                if (xData.length > 0) {
                    var startValue = xData[0];
                    var endValue = xData[xData.length - 1];
                    isSettingZoom = true;
                    chart_ins.dispatchAction({
                        type: 'dataZoom',
                        startValue: startValue,
                        endValue: endValue
                    });
                    isSettingZoom = false;
                }
            }
            """,
        )
        
class Exchange(ExchangeBase):
    def __init__(self, trade_symbols, fee=0.0002, initial_balance=10000, recorded=False):
        super().__init__(initial_balance=initial_balance, recorded=recorded)
        self.fee = fee
        self.trade_symbols = trade_symbols
        self.id_gen = 0
        self.account['USDT'].update({
            'hold': 0,
            'long': 0,
            'short': 0
        })
        for symbol in trade_symbols:
            self.account[symbol] = {'amount': 0, 'hold_price': 0, 'value': 0, 'price': 0,
                                     'realised_profit': 0, 'unrealised_profit': 0, 'fee': 0}

    def Trade(self, symbol, direction, price, amount, **kwargs):
        if self.recorded and 'time' not in kwargs:
            raise ValueError("Time parameter is required in recorded mode.")

        time = kwargs.get('time', pd.Timestamp.now())

        self.id_gen += 1
        tid = len(self.trades) if self.recorded else self.id_gen

        trade = {
            'symbol': symbol,
            'exchange': "local",
            'orderid': tid,
            'tradeid': tid,
            'direction': direction,
            'price': price,
            'volume': abs(amount),
            'datetime': time,
            'gateway_name': "local",
            'pos': 0  # 初始化盈亏
        }

        if symbol not in self.trade_symbols:
            self.trade_symbols.append(symbol)
            self.account[symbol] = {'amount': 0, 'hold_price': 0, 'value': 0, 'price': 0,
                                     'realised_profit': 0, 'unrealised_profit': 0, 'fee': 0}

        cover_amount = 0 if direction * self.account[symbol]['amount'] >= 0 else min(abs(self.account[symbol]['amount']), amount)
        open_amount = amount - cover_amount

        if cover_amount > 0 and np.isnan(price):
            print(f'{symbol} 可能已经下架, 清仓')
            price = self.account[symbol]['price'] if self.account[symbol]['price'] != 0 else self.account[symbol]['hold_price']
        else:
            if np.isnan(price) or np.isnan(amount):
                print(f'{symbol} 价格或者数量为nan, 交易忽略')
                return

        # 扣除手续费
        self.account['USDT']['realised_profit'] -= price * amount * self.fee
        self.account['USDT']['fee'] += price * amount * self.fee
        self.account[symbol]['fee'] += price * amount * self.fee

        if cover_amount > 0:  # 先平仓
            profit = -direction * (price - self.account[symbol]['hold_price']) * cover_amount
            self.account['USDT']['realised_profit'] += profit  # 利润
            self.account[symbol]['realised_profit'] += profit
            self.account[symbol]['amount'] -= -direction * cover_amount
            trade['pos'] = profit  # 记录盈亏
            self.account[symbol]['hold_price'] = 0 if self.account[symbol]['amount'] == 0 else self.account[symbol]['hold_price']

        if open_amount > 0:
            total_cost = self.account[symbol]['hold_price'] * direction * self.account[symbol]['amount'] + price * open_amount
            total_amount = direction * self.account[symbol]['amount'] + open_amount

            self.account[symbol]['hold_price'] = total_cost / total_amount
            self.account[symbol]['amount'] += direction * open_amount

        if kwargs:
            self.opt.update(kwargs)

        # 记录账户总资产到 history
        if self.recorded:
            self.opt['trades'].append(trade)
            self.record_history(time)

        # 自动更新账户状态
        self.Update({symbol: price},  time=time)

        return trade

    def Buy(self, symbol, price, amount, **kwargs):
        return self.Trade(symbol, 1, price, amount, **kwargs)

    def Sell(self, symbol, price, amount, **kwargs):
        return self.Trade(symbol, -1, price, amount, **kwargs)

    def CloseAll(self, price, symbols=None, **kwargs):
        if symbols is None:
            symbols = self.trade_symbols
        trades = []
        symbols = [s for s in symbols if s in self.account and self.account[s]['amount'] != 0]
        for symbol in symbols:
            if symbol not in price or np.isnan(price[symbol]):
                print(f'{symbol} 可能已经下架')
                price[symbol] = self.account[symbol]['price'] if self.account[symbol]['price'] != 0 else self.account[symbol]['hold_price']
            if np.isnan(price[symbol]):
                price[symbol] = self.account[symbol]['price'] if self.account[symbol]['price'] != 0 else self.account[symbol]['hold_price']

            direction = -np.sign(self.account[symbol]['amount'])
            trade = self.Trade(symbol, direction, price[symbol], abs(self.account[symbol]['amount']), **kwargs)
            trades.append(trade)
        return trades

    def _recalc_aggregates(self):
        """基于 self.account 中已保存的各 symbol 状态，重算聚合字段。"""
        usdt = self.account['USDT']
        usdt['unrealised_profit'] = 0
        usdt['hold'] = 0
        usdt['long'] = 0
        usdt['short'] = 0

        for symbol in self.trade_symbols:
            if symbol not in self.account:
                continue
            sym = self.account[symbol]
            px = sym.get('price', 0)
            amt = sym.get('amount', 0)
            hp = sym.get('hold_price', 0)

            # 仅当价格有效时计入聚合
            if px is not None and not np.isnan(px) and px != 0:
                sym['unrealised_profit'] = (px - hp) * amt
                sym['value'] = amt * px

                if amt > 0:
                    usdt['long'] += sym['value']
                elif amt < 0:
                    usdt['short'] += sym['value']

                usdt['hold'] += abs(sym['value'])
                usdt['unrealised_profit'] += sym['unrealised_profit']

        usdt['total'] = round(self.account['USDT']['realised_profit'] + self.initial_balance + usdt['unrealised_profit'], 6)
        usdt['leverage'] = round(usdt['hold'] / usdt['total'] if usdt['total'] != 0 else 0.0, 3)

    def Update(self, close_price=None, symbols=None, partial=True, **kwargs):
        """
        更新账户状态。
        - partial=True：只更新给定 symbols 的逐符号状态，然后对所有符号做一次聚合重算（推荐）。
        - partial=False：与原逻辑兼容；当提供一部分 symbol 时，也会聚合重算，不会清空未提供符号的信息。
        
        支持三种入参形式：
        1) close_price 为 dict/Series：symbols 自动取其键/索引
        2) close_price 为标量 + symbols 为单个字符串
        3) 显式传 symbols=list[...]，close_price 为 dict/Series（从中取价）
        如果既不传 close_price 也不传 symbols，则只做一次聚合重算（例如你先前已经手动修改了某些 symbol 的 price）。
        """
        if self.recorded and 'time' not in kwargs:
            raise ValueError("Time parameter is required in recorded mode.")

        time = kwargs.get('time', pd.Timestamp.now())

        # 解析 symbols & 价格获取器
        if symbols is None:
            if isinstance(close_price, dict):
                symbols = list(close_price.keys())
            elif isinstance(close_price, pd.Series):
                symbols = list(close_price.index)
            else:
                symbols = []
        elif isinstance(symbols, str):
            symbols = [symbols]

        def get_px(sym):
            if isinstance(close_price, (int, float, np.floating)) and len(symbols) == 1:
                return float(close_price)
            if isinstance(close_price, dict):
                return close_price.get(sym, np.nan)
            if isinstance(close_price, pd.Series):
                return close_price.get(sym, np.nan)
            return np.nan

        # 仅更新传入的 symbols（部分更新，不动其它符号已保存信息）
        for sym in symbols:
            if sym not in self.trade_symbols or sym not in self.account:
                # 未登记的交易对直接跳过（或可选择自动登记，但此处保持严格）
                continue
            px = get_px(sym)
            if px is None or np.isnan(px):
                # 价格无效则不覆盖旧价格
                continue

            self.account[sym]['price'] = float(px)
            amt = self.account[sym]['amount']
            self.account[sym]['value'] = amt * float(px)
            # 不在这里算 unrealised_profit，聚合阶段统一算

        # 无论 partial 与否，最后都用“账户中保存的所有 symbol 当前状态”做一次聚合重算
        self._recalc_aggregates()

        # 记录账户总资产到 history
        if self.recorded:
            self.record_history(time)

# e = Exchange([])
# e.Sell('DOGEUSDT', 0.3, 3)
# print(e.account)

def gen_back_time(start_date, end_date, train_period_days, test_period_days):
    # 将输入的日期字符串转换为时间戳
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    
    # 定义训练和测试周期
    train_period = pd.Timedelta(days=train_period_days)
    test_period = pd.Timedelta(days=test_period_days)
    
    # 存储训练和测试日期区间
    train_date = []
    test_date = []
    
    # 确定训练和测试的时间区间
    current_date = start_date
    while current_date + test_period <= end_date:
        tsd_start = current_date
        tsd_end = tsd_start + test_period
        trd_end = tsd_start
        trd_start = trd_end - train_period
        
        train_date.append((pd.Timestamp(trd_start.date()), pd.Timestamp(trd_end.date())))
        test_date.append((pd.Timestamp(tsd_start.date()), pd.Timestamp(tsd_end.date())))
        
        # 移动到下一个测试周期的开始
        current_date = tsd_end
    
    # 将其转换为DataFrame
    train_date = pd.DataFrame(train_date, columns=['x_start', 'x_end'])
    test_date = pd.DataFrame(test_date, columns=['y_start', 'y_end'])
    back_df = pd.concat([train_date, test_date], axis=1)
    return back_df