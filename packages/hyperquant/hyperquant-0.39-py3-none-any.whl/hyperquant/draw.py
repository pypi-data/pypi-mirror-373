import pathlib
import uuid
import pandas as pd
import os
from pyecharts.charts import Line, Grid, Kline, Bar
from pyecharts import options as opts
from pyecharts.commons.utils import JsCode
import webbrowser

top_height = 45  # 图表最上面标题区高度
h_space = 3  # 每个曲线图之间的间隔
left_data_div_width = 400  # 左侧数据显示区宽度


# left_tl_width=100  # 左侧图例


def draw(
    df: pd.DataFrame,
    data_dict: list,
    date_col: str,
    date_formate: str = "%Y-%m-%d %H:%M:%S",
    pic_width: int = 1500,
    title: str = "数据查看",
    path: str = None,
    show: bool = True,
    display_js=None,
    auto_play_space="",
    play_ibe_js="",
    height_type: str = "px",
    zoom_space=100,
    zoom_end=None,
    right_width=300,
    right_data_view=True,
):
    """
    :param df: 必填,包含净值的数据字典格式
    :param data_dict: 必填,要显示的每个图表的配置,具体配置中的属性如下：[{
        df:df,  # 不必填,如果不填,表示本图表的数据为入参df,如果本属性有值表示本图表的数据在另一个df中
        series_name: 不必填,因子显示名称,如果为空,则跟col一样。
        col: 不必填,df中的列名,如果是K线则为["open", "close", "lowest", "highest"]的各列名,如果为穿鞋,则跟series_name一样
        draw_type:"Kline",  默认Line,图表格式,有Kline(K线),Line(曲线),Bar(柱状图),DownLine(回撤图)
        can_change_log:False, 默认False,是否可以转换对数值显示
        height:200, 默认200,图表高度
        is_smooth:True, 默认为True,曲线是否平滑显示,本参数只对曲线有效
        is_symbol_show:False, 默认为False,曲线或回撤图是否显示点,本参数只对曲线和回撤图有效
        check_col, 不必填,如果是Bar有可能显示的是成交量成交额之类的,需要当前涨显示红色,跌显示绿色,本属性是表示df中哪一列表示涨跌幅,或可以用来判断柱状图颜色
        color: 不必填,线的颜色,默认自动分配颜色
        window_cumprod_base_one: 不必填,默认为False。可见窗口里是否从1开始算净值,本配置只对曲线生效,一般用在原曲线数据是涨跌幅,并且在可见的窗口里总是从1开始累计净值的情况
        split_color_col: 不必填,默认为None。与color属性冲突。轮动资金曲线或净值曲线需要根据不同的子策略分段显示不同的颜色时使用,本属性表示用df中的哪个列判断子策略。上面是业务角度的描述,通用的描述就是曲线需要根据df中的某列显示不同的颜色场景。
        split_color: 不必填,默认为None。与color属性冲突。如果split_color_col有值,则本参数一定要配置。当split_color_col有值时,可以配置本属性,用来描述每个子策略对应的颜色
        trade_single: 不必填,默认为None,买入卖出信号列,如果该属性配置了,则图上会根据该列的值如果为1显示做多,如果为-1显示做空,0表示平仓
        kline_color_type: 不必填,默认为True,表示K线的颜色方式,True为涨红跌绿,False为涨绿跌红
        dec_length:不必填,默认为None,表示显示本曲线的数据时显示小数的位数,None为不控制
        },...]
    :param date_col: 必填,时间列的名字,如果为None将用索引作为时间列
    :param date_formate: 不必填,默认为%Y-%m-%d %H:%M:%S "年-月-日 时:分:秒"时间列显示格式
    :param pic_width: 不必填,默认为1500,图表的宽度,注：图表的高度会根据data_dict中的每个图表的高度自动算出
    :param title: 不必填,默认为“数据查看”,整体表图标题
    :param path: 不必填,默认为当前代码所在目录的chart.html,图片路径
    :param show: 不必填,默认为True,是否打开图片
    :param display_js: 不必填,默认为None,右侧扩展信息区显示处理,js内容中必须包括function set_ext_data_div(ext_data_div,zoom_end,zoom_space)函数
    :param auto_play_space: 不必填,自动播放间隔时间计算函数,必须是js函数,js中必须包括function auto_play_space(xi)函数,返回值的单位为毫秒
    :param play_ibe_js: 不必填,跳转或自动播放时,需要自动跳一下跳的下一个时间范围,比如整个时间范围一次移动一个持股周期,必须是js函数,js中必须包括play_ibe_js(ibe,next),ibe当前区间begin和end,next为true表示周期范围向后跳,next为false表示 周期范围向前跳
    :param height_type: 子图的高度数据类型,有%和px两种,如果值为%表示data_dict中子图的height值代表百分比,否则代表px
    :param zoom_space: 不必填,默认值 20,初始X轴窗口显示日期周期数
    :param zoom_end: 不必填,默认值 None,X轴窗口默认结束点
    :param right_width: 不必填,默认值 300,右侧信息显示区的宽度
    :param right_data_view:不必填,默认为True,表示右侧信息显示区是否显示曲线的数据
    """
    draw_df = df
    time_data = _produce_x_date(draw_df, date_col, date_formate)  # 计量时间轴
    global left_data_div_width
    left_data_div_width = right_width  # 右侧数据显示区宽度
    # left_all_width = left_data_div_width  # 图表左侧区域宽度,如果扩展区别不显示内容,则为数据显示区的1倍,否则为2倍
    # if display_js is not None:
    #     left_all_width = left_all_width * 2
    # 设置入参的默认值,同时计算整个图表的高度
    # pre_height = 100 / (len(data_dict) + 1)
    # 设置data_dict中的默认值,计算出的整个图表的高度all_h（只在height_type为px时all_h值才有意义）,同时如果所有子图都未设置高度height_type会被强制设成%
    data_dict, all_h, height_type = _set_default_value(data_dict, height_type)
    if height_type == "%":
        grid_height = "100%"
    else:
        grid_height = f"{all_h}px"
    grid_chart = Grid(
        init_opts=opts.InitOpts(
            width=f"100%",
            height=grid_height,
            animation_opts=opts.AnimationOpts(
                animation=True, animation_easing="linear"
            ),
            page_title=title,
            # renderer=RenderType.SVG,
        ),
    )
    i = 0
    js_code = ""  # 额外配置参数、对数显示转换等html和javascript脚本
    js_data_item = "var line_other_param=["
    if height_type == "%":
        cur_top = 0
    else:
        cur_top = top_height  # 当前空白区域的最上面纵坐标
    # 循环处理每个图表的显示参数
    visual_map_all_js = ""
    mark_point_js_all = ""
    ii = 0
    for data_item in data_dict:
        # 把图表加到grid中
        line, sub_js_code, visual_map_js, mark_point_js = _produce_one_chart(
            grid_chart,
            draw_df,
            data_item,
            time_data,
            cur_top,
            title,
            len(data_dict),
            i,
            pic_width,
            height_type,
            data_dict,
            ii,
            df,
            date_col,
        )  # 创建每个图表的配置信息
        js_data_item += sub_js_code
        visual_map_all_js += visual_map_js
        mark_point_js_all += mark_point_js
        if "sub_chart" in data_item:
            for sub_data_item in data_item["sub_chart"]:
                sub_line, sub_js_code, visual_map_js, mark_point_js = (
                    _produce_one_chart(
                        grid_chart,
                        draw_df,
                        sub_data_item,
                        time_data,
                        cur_top,
                        title,
                        1,
                        1,
                        pic_width,
                        height_type,
                        data_dict,
                        ii,
                        df,
                        date_col,
                    )
                )
                ii += 1
                js_data_item += sub_js_code
                visual_map_all_js += visual_map_js
                mark_point_js_all += mark_point_js
                line.overlap(sub_line)
        if height_type == "%":
            pos_bottom = ""
            if i == 0:
                pos_bottom = f"{100 - data_item['height']}%"
            if i == len(data_dict) - 1:
                pos_bottom = "80"
            if i == 0:
                grid_chart.add(
                    line,
                    grid_opts=opts.GridOpts(
                        pos_left="45",
                        pos_right=f"{left_data_div_width + 80}",
                        pos_top=top_height,
                        pos_bottom=pos_bottom,
                    ),
                )
            elif i == len(data_dict) - 1:
                grid_chart.add(
                    line,
                    grid_opts=opts.GridOpts(
                        pos_left="45",
                        pos_right=f"{left_data_div_width + 80}",
                        pos_top=f"{cur_top}%",
                        pos_bottom=pos_bottom,
                    ),
                )
            else:
                grid_chart.add(
                    line,
                    grid_opts=opts.GridOpts(
                        pos_left="45",
                        pos_right=f"{left_data_div_width + 80}",
                        pos_top=f"{cur_top}%",
                        height=f"{data_item['height']}%",
                    ),
                )
        else:
            if i == 0:
                grid_chart.add(
                    line,
                    grid_opts=opts.GridOpts(
                        pos_left="45",
                        pos_right=f"{left_data_div_width + 80}",
                        pos_top=cur_top,
                        height=data_item["height"],
                    ),
                )
            elif i == len(data_dict) - 1:
                grid_chart.add(
                    line,
                    grid_opts=opts.GridOpts(
                        pos_left="45",
                        pos_right=f"{left_data_div_width + 80}",
                        pos_top=cur_top,
                        height=data_item["height"],
                    ),
                )
            else:
                grid_chart.add(
                    line,
                    grid_opts=opts.GridOpts(
                        pos_left="45",
                        pos_right=f"{left_data_div_width + 80}",
                        pos_top=cur_top,
                        height=data_item["height"],
                    ),
                )
        # 曲线类型的图表 加上切换 对数显示 的相关脚本
        if data_item["draw_type"] == "Line" or data_item["draw_type"] == "Bar":
            js_code = js_code + _produce_change_log_js(
                data_item, cur_top, i, height_type
            )
        cur_top = cur_top + data_item["height"]  # 更新当前空白区域的最上面top
        i = i + 1
        ii += 1
    js_code += f"""
        <script>
        function fixDecLen(fd,dec_length){{
            //line_other_param[i].dec_length
            if (dec_length>=0){{
                let dzz=10 ** dec_length;
                fd=Math.round(fd * dzz) / dzz;
                //fd=fd.toFixed(dec_length);
            }}
            return fd;
        }}        
        {js_data_item}
        ];
        var cc=document.getElementsByClassName("chart-container");
        var cc_name=cc[0].id;
        var chart_ins=window["chart_"+cc_name];
        var dataZoom_startValue_i=0;
        var dataZoom_endValue_i=0;
        var dataZoom_startValue=0;
        var dataZoom_endValue=0;
        var chart_option=window["option_"+cc_name];
        var chart_option_back=JSON.parse(JSON.stringify(chart_option));
    """
    if len(visual_map_all_js) > 0:
        js_code += f"""
            chart_option["visualMap"]=[
                {visual_map_all_js}
            ];
        """
    if len(mark_point_js_all) > 0:
        js_code += mark_point_js_all
    js_code += _produce_tooltip_formatter()
    # if len(visual_map_all_js) + len(mark_point_js_all) > 0:
    js_code += """
        chart_ins.setOption(chart_option);
    """
    if display_js is not None:
        js_code += f"""
        {display_js}
        """
    if auto_play_space is not None:
        js_code += f"""
        {auto_play_space}
        """
    if play_ibe_js is not None:
        js_code += f"""
        {play_ibe_js}
        """
    js_code += "</script>\n"
    js_code = js_code + _produce_date_opt_js(
        pic_width, display_js, height_type, title, zoom_space, zoom_end, right_data_view
    )  # 生成日期跳转相关的脚本
    # 生成网页内容并写到html文件中
    if path is None:  # 默认写入到当前文件夹的chart.html中
        path = os.path.abspath(os.path.dirname(__file__)) + "/chart.html"
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"{grid_chart.render_embed()}{js_code}")
    if show:
        path = pathlib.Path(path).absolute().as_uri()
        webbrowser.open(path)


def _set_default_value(data_dict, height_type):
    # px和百分比两种指定高度的模式,不能混用,用一个入参控制。
    # 1.用px指定高度：页面会向下变长,没有指定的子图高度默认200；
    # 2.用 % 指定高度：所有子图在高度上刚好撑满屏幕,第一个图要让40px出来显示上面标题等内容；没有指定的子图高度用剩下的高度平分,
    # 3.所有子图都未指定高度：不管height_type是什么类型,第一个图是其它所有图的双倍高,其它图一样高,用百分比,撑满屏幕。
    all_h = top_height  # 整个图表的高度
    set_height = 0  # 配置了height的所有子图的高度汇总值
    set_height_num = 0  # 配置了height的所有子图的个数
    for data_item in data_dict:
        if "height" in data_item:
            set_height += data_item["height"]
            set_height_num += 1
    if set_height == 0:
        height_type = "%"
        def_height = int(100 / (len(data_dict) + 1))
    else:
        if height_type == "%" and (len(data_dict) - set_height_num) > 0:
            def_height = int((100 - set_height) / (len(data_dict) - set_height_num))
        else:
            def_height = 200
    i = 0
    for data_item in data_dict:
        if "height" not in data_item:
            if i == 0 and set_height == 0:
                data_item["height"] = def_height * 2
            else:
                data_item["height"] = def_height
        _set_data_item_value(data_item)
        if "sub_chart" in data_item:
            for sub_data in data_item["sub_chart"]:
                _set_data_item_value(sub_data)
        all_h = all_h + data_item["height"]  # + h_space
        i += 1
    all_h = all_h + 80  # - h_space  # 在最后一个图表的后面加50,用来显示时间选择轴
    return data_dict, all_h, height_type


def _set_data_item_value(data_item):
    if "series_name" not in data_item:
        if "col" in data_item:
            data_item["series_name"] = data_item["col"]
        else:
            raise ValueError("数据显示项的配置中不能series_name和col都为空")
    if "draw_type" not in data_item:
        data_item["draw_type"] = "Line"
    if "is_smooth" not in data_item:
        data_item["is_smooth"] = True
    if "is_symbol_show" not in data_item:
        data_item["is_symbol_show"] = False
    if "kline_color_type" not in data_item:
        data_item["kline_color_type"] = True
    if "dec_length" not in data_item:
        data_item["dec_length"] = None


def _produce_one_chart(
    grid_chart,
    draw_df,
    data_item,
    time_data,
    cur_top,
    title,
    chart_count,
    i,
    pic_width,
    height_type,
    data_dict,
    ii,
    main_df,
    date_col,
):
    """
    生成一个图表的绘图配置
    :param grid_chart: 整合所有图表的grid组件
    :param draw_df: 本图表使用的数据集
    :param data_item: 本图表的入参配置
    :param time_data: 图表时间轴数据
    :param cur_top: 当前空白区域最上面的纵坐标
    :param title: 图表title
    :param chart_count: 总计图表数,主要用在生成第一个图表时配置项中的多表联动部分需要知道一共有多少个图表
    :param i: 当前是第几个图表,主要用在判断是否是第一个图表,如果是第一个图表需要做多表联动相关的配置
    """
    js_code = f"{{name:'{data_item['series_name']}',"
    if "window_cumprod_base_one" in data_item and data_item["window_cumprod_base_one"]:
        js_code += f"window_cumprod_base_one:true,"
    else:
        js_code += f"window_cumprod_base_one:false,"
    if "color" in data_item:
        js_code += f"color:'{data_item['color']}',"
    if "dec_length" in data_item and data_item["dec_length"] is not None:
        js_code += f"dec_length:{data_item['dec_length']},"
    else:
        js_code += f"dec_length:-1,"
    js_code += "},"
    if "df" in data_item:
        draw_df = data_item["df"]
    # 计算当前图表的显示数据列
    if "col" in data_item:  # 如果没有列名,则表示列名与显示名一致
        col = data_item["col"]
    else:
        if data_item["draw_type"] == "Kline":
            col = ["open", "close", "lowest", "highest"]
        else:
            col = data_item["series_name"]
    if "draw_type" in data_item and data_item["draw_type"] == "Kline":
        line = Kline()
    elif "draw_type" in data_item and data_item["draw_type"] == "Bar":
        line = Bar()
    else:
        line = Line()
    line.add_xaxis(time_data)  # 设置图表横轴为时间轴
    if "color" in data_item:
        linestyle_opts = opts.LineStyleOpts(color=data_item["color"])
        itemstyle_opts = opts.ItemStyleOpts(color=data_item["color"])
    else:
        linestyle_opts = opts.LineStyleOpts()
        itemstyle_opts = opts.ItemStyleOpts()
    if data_item["draw_type"] == "Kline":
        data_list = draw_df[col].to_numpy().tolist()
        if not data_item["kline_color_type"]:
            itemstyle_opts = opts.ItemStyleOpts(
                color="#14b143",
                color0="#ef232a",
                border_color="#14b143",
                border_color0="#ef232a",
            )
        else:
            itemstyle_opts = opts.ItemStyleOpts(
                color="#ef232a",
                color0="#14b143",
                border_color="#ef232a",
                border_color0="#14b143",
            )
        line.add_yaxis(
            data_item["series_name"], data_list, itemstyle_opts=itemstyle_opts
        )
    elif data_item["draw_type"] == "Bar":
        if "check_col" in data_item:
            random_uuid = str(uuid.uuid4()).replace("-", "")
            line.add_yaxis(
                series_name=data_item["series_name"],
                y_axis=draw_df[col].tolist(),
                label_opts=opts.LabelOpts(is_show=False),
                itemstyle_opts=opts.ItemStyleOpts(
                    color=JsCode(
                        f"""
                                    function(params) {{\n
                                        var colorList;
                                        if (check_{random_uuid}[params.dataIndex] > 0) {{
                                            colorList = '#ef232a';
                                        }} else {{
                                            colorList = '#14b143';
                                        }}
                                        return colorList;
                                    }}
                                    """
                    )
                ),
            )
            grid_chart.add_js_funcs(
                f"var check_{random_uuid} = {draw_df[data_item['check_col']].tolist()}"
            )
        else:
            line.add_yaxis(
                series_name=data_item["series_name"],
                y_axis=draw_df[col].tolist(),
                label_opts=opts.LabelOpts(is_show=False),
                itemstyle_opts=itemstyle_opts,
            )
    elif data_item["draw_type"] == "DownLine":
        line.add_yaxis(
            series_name=data_item["series_name"],
            y_axis=draw_df[col].tolist(),
            itemstyle_opts=opts.ItemStyleOpts(
                color="#fdd07d", border_color="#fdd07d", border_width=0
            ),
            is_symbol_show=data_item["is_symbol_show"],
            areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
            linestyle_opts=linestyle_opts,
            label_opts=opts.LabelOpts(is_show=False),
        )
    else:
        line.add_yaxis(
            series_name=data_item["series_name"],
            y_axis=draw_df[col].tolist(),
            is_smooth=data_item["is_smooth"],
            label_opts=opts.LabelOpts(is_show=False),
            is_symbol_show=data_item["is_symbol_show"],
            linestyle_opts=linestyle_opts,
            itemstyle_opts=itemstyle_opts,
        )

    if i == 0:  # 如果是第0个图表,要设置一系列的参数实现后面的多图联动
        _set_first_chart(line, title, cur_top, chart_count, i, pic_width, height_type)
    else:
        _set_other_chart(line, cur_top, chart_count, i, pic_width, height_type)
    virtual_map_js = produce_split_color_js(
        draw_df, data_item, ii
    )  # 生成曲线分段显示不同颜色的配置
    mark_point_js = _produce_mark_point(
        main_df, date_col, draw_df, data_item, ii, time_data
    )
    return line, js_code, virtual_map_js, mark_point_js


def _produce_x_date(draw_df: pd.DataFrame, date_col: str, date_formate: str) -> list:
    """
    计算时间轴数据
    :param draw_df:数据集
    :param date_col: 日期列名
    :param date_formate: 日期显示格式
    """
    # 计算时间轴,如果传入了data_col,则取该列作为时间轴,否则取index作为时间轴
    if date_col:
        if hasattr(draw_df[date_col], "dt"):
            time_data = draw_df[date_col].dt.strftime(date_formate).tolist()
        else:
            time_data = draw_df[date_col].tolist()
    else:
        if hasattr(draw_df[date_col], "dt"):
            time_data = draw_df.index.dt.strftime(date_formate).tolist()
        else:
            time_data = draw_df.index.tolist()
    return time_data


def _produce_change_log_js(data_item, cur_top, i, height_type) -> str:
    """
    给当前图表加上切换 对数显示 的相关脚本
    :param data_item: 当前图表配置信息
    :param cur_top: 当前空白区域最上面的纵坐标
    :param i: 当前是第几个图表
    """
    js_code = ""
    if height_type == "%":
        top = f"{cur_top}%"
    else:
        top = f"{cur_top}px"
    if "can_change_log" in data_item and data_item["can_change_log"]:
        # 添加 JavaScript 代码实现切换坐标系功能
        js_code = f"""
            <div style='position: absolute;top: {top};right:{left_data_div_width + 120}px'>
                <select id="log_select_{i}" style="font-size: 15px;width: 70px;height: 30px;">
                    <option value="value">线性</option>
                    <option value="log">对数</option>
                </select>
            </div>
            <script>
            document.getElementById('log_select_{i}').onchange = function(){{
                let cc=document.getElementsByClassName("chart-container");
                let cc_name=cc[0].id;
                let option=window["option_"+cc_name];
                option.yAxis[{i}].type=this.value;
                let ccv=window["chart_"+cc_name];
                ccv.setOption(option);        
            }}
            </script>

        """
    return js_code


def _produce_date_opt_js(
    pic_width: int,
    display_js: str,
    height_type: str,
    title,
    zoom_space,
    zoom_end,
    right_data_view,
):
    """
    生成日期跳转操作相关的脚本
    """
    display_ext = "none"  # 扩展数据区是否显示
    ext_data_div_width = 0  # 扩展数据区显示宽度
    if display_js is not None:
        display_ext = ""
        ext_data_div_width = left_data_div_width
    view_data_js = f"""
                let data_div = document.getElementById('data_div');    
                let conn= "<table style='font-size: 12px;word-break: break-word;width:100%'>"
                            +"<tr><td style='background-color: #f7f7f7;;border-right: 1px dashed #000;padding: 5px 0;font-weight: bold;'>当前时间</td>"
                            +"<td style='background-color: #f7f7f7;'>"+chart_option.xAxis[0].data[ei]+"</td>"
                for (let i=0;i<chart_option.series.length;i++){{
                    let b_color= "color" in line_other_param[i]?line_other_param[i].color:"#101010";
                    // b_color = darkenColor(b_color); //本来是准备给颜色减淡一些做背景的,有问题先不处理了
                    conn = conn + "<tr><td style='color:"+b_color+";background-color:#f7f7f7;border-right: 1px dashed #000;border-top: 1px dashed #000;padding: 1px 0;font-weight: bold;'>"
                            +chart_option.series[i].name+"</td><td style='border-top: 1px dashed #000;'>";
                    let datacon="";
                    let d=chart_option.series[i].data[ei];
                    let dec_length=line_other_param[i].dec_length;
                    if (chart_option.series[i].type=="line"){{
                        d=d[1];
                        d=fixDecLen(d,dec_length);
                        datacon+="<span style='color:"+(d>0?"red":"green")+"'>"+d+"</span>";
                    }}else if (chart_option.series[i].type=="candlestick"){{
                        let zdf=d[1]/d[0]-1;
                        zdf=(zdf*100).toFixed(2);
                        datacon+="开("+fixDecLen(d[0],dec_length)+"),收("+fixDecLen(d[1],dec_length)+"),<br/>低("
                            +d[2]+"),高("+fixDecLen(d[3],dec_length)+"),<br/>涨:<span style='color:"+(zdf>0?"red":"green")+"';>"
                            +fixDecLen(zdf,dec_length)+"%</span>";
                    }}else{{
                        datacon+=d;
                    }}
                    conn = conn + datacon;
                    conn = conn +"</td></tr>"
                }}
                conn = conn + "</table>";
                data_div.innerHTML = conn;
    """
    js_code = f"""
        <style>
        body {{
            margin: 0;
        }}  
        .button {{
            border: 0px solid #ccc; /* 设置按钮的边框 */
            background-color: transparent; /* 设置按钮的背景颜色为透明 */
            padding: 5px 10px 5px 10px; /* 设置按钮的内边距 */
            cursor: pointer; /* 设置按钮的鼠标样式为手型 */
            font-size: 13px; /* 设置按钮的字体大小 */
        }}
        .button:hover {{
            background-color: darkorange; /* 设置按钮在鼠标悬停时的背景颜色 */
            color: white;
        }}
        </style>
        <div style="position: fixed;left: 40px;top: 40px;bottom: 0;width: 3px;background-color: #e0e3eb;"></div>
        <div style="position: fixed;right: {left_data_div_width}px;top: 40px;bottom: 0;width: 3px;background-color: #e0e3eb;"></div>
        <div style="position: fixed;left: 0;right:0;top: 40px;height: 3px;background-color: #e0e3eb;"></div>
        <div style="position: fixed;left: 0px;height: 40px;top: 0;right: 0;background-color:#f9f9f9;display: flex;">
            <div style="padding: 10px 10px 5px 5px;font-size: 16px;font-weight: bold;">{title}</div>
            <div style="margin: 8px 0px;width: 1px;height:25px;background-color: #b4b8c3;"></div>
            <div style='display: flex;padding: 5px;font-size: 13px;'>
                <label for="date-input" style="padding-top: 7px;">日期：</label>
                <input id="date-input" name="date" style="width:80px">
                <button class="button" type="submit" id="jump_bt">跳转</button>
                <button class="button" style="display: flex;padding-top: 7px;" type="submit" id="to_front">
                    ➡️&#x3000
                    <span>前进</span>
                </button>
                <button class="button" style="display: flex;padding-top: 7px;" type="submit" id="to_back">
                    ⬅️&#x3000
                    <span>回退</span>
                    
                </button>
                <button class="button" type="submit" id="auto_play">自动前进</button>
            </div>
            <div style="margin: 8px 0px;width: 1px;height:25px;background-color: #b4b8c3;"></div>
            <div style='display: flex;padding: 5px;font-size: 13px;'>
                <label for="date-input" style="padding-top: 7px;">时间窗口宽度：</label>
                <input id="date_win_width" name="date_win_width" style="width:60px">
                <button class="button" type="submit" id="date_win_width_set">设置</button>
            </div>
            <div style="margin: 8px 0px;width: 1px;height:25px;background-color: #b4b8c3;"></div>
            <div id="inf_div" style='border: 0px solid black;font-size:14px;color: red;padding: 10px;'>
            信息显示区
            </div>
        </div>

        <div id="all_data_div" style='position: absolute;top: 45px;right:0px;width:{left_data_div_width}px;height:auto;border: 0px solid black;font-size:14px;'>
            <div id="data_div" style='display:{"" if right_data_view else "none"};'>
            数据显示区
            </div>
            <div style="left: 0;right:0;height: 3px;background-color: #e0e3eb;display:{"" if right_data_view else "none"};"></div>
            <div id="ext_data_div" style='display:{display_ext};width:{ext_data_div_width}px;border: 0px solid black;font-size:14px;'>
            扩展信息显示
            </div>
            <div style="display:{display_ext};left: 0;right:0;height: 3px;background-color: #e0e3eb;"></div>
        </div>
        <script>
            //获取chart实例
            function play_ibe_js_default(ibe,next){{
                //如果next为true表示向后移动,false为向前移动,null为不移动
                if(next===true){{
                    ibe.begin += 1
                    ibe.end += 1;
                }}else if(next===false){{
                    ibe.begin -= 1
                    ibe.end -= 1;
                }}
                ibe.begin = ibe.begin<0?0:ibe.begin;
                ibe.end = ibe.end<10?10:ibe.end;
                return ibe;
            }}
            
            function play_ibe(ibe,next){{
                if (typeof play_ibe_js=="function"){{
                    return play_ibe_js(ibe,next);
                }}else{{
                    return play_ibe_js_default(ibe,next);
                }}
            }}
            
            function cleanInf(){{
                document.getElementById("inf_div").innerHTML=""
            }}
            function setInf(info,view_sed){{
                document.getElementById("inf_div").innerHTML=info
                if (view_sed!=null && view_sed>0){{
                    setTimeout(cleanInf, 5000); // 1000毫秒后清除提示
                }}
            }}
            function darkenColor(colorStr, percent) {{
                const f = parseInt(colorStr.slice(1), 16);
                const t = (f * percent) >> 16;
                return "#" + (0x10000 + t).toString(16).slice(1);
            }}

            // 监听 datazoom 事件
            chart_ins.on('datazoom', function (params) {{
                // 获取当前 dataZoom 的 startValue 和 endValue
                date_data=chart_option.xAxis[0].data;
                let bi=0,ei=0;
                if (params.start>=0){{
                    dataZoom_startValue_i = Math.ceil(date_data.length*params.start/100);
                    dataZoom_startValue_i=dataZoom_startValue_i<0?0:dataZoom_startValue_i;
                    dataZoom_endValue_i = Math.ceil(date_data.length*params.end/100);
                    dataZoom_endValue_i=dataZoom_endValue_i>date_data.length-1?date_data.length-1:dataZoom_endValue_i;
                    bi = dataZoom_startValue_i;
                    ei = dataZoom_endValue_i;
                    dataZoom_startValue="";
                    dataZoom_endValue="";
                    // 输出 startValue 和 endValue
                    //console.log("startValue:", date_data[dataZoom_startValue_i]);
                    //console.log("endValue:", date_data[dataZoom_endValue_i]);
                }}else{{
                    dataZoom_startValue=params.startValue;
                    dataZoom_endValue=params.endValue;
                    dataZoom_startValue_i=-1;
                    dataZoom_endValue_i=-1;
                    for (let i=0;i<chart_option.xAxis[0].data.length;i++){{
                        if (chart_option.xAxis[0].data[i]==dataZoom_startValue){{
                            bi=i;
                        }}
                        if (chart_option.xAxis[0].data[i]==dataZoom_endValue){{
                            ei=i;
                        }}
                    }}
                    dataZoom_startValue_i=bi;
                    dataZoom_endValue_i=ei;
                    // 输出 startValue 和 endValue
                    //console.log("startValue:", dataZoom_startValue);
                    //console.log("endValue:", dataZoom_endValue);
                }}
                dataZoom_endValue_i=ei;
                //归1化显示设置window_cumprod_base_one的数据,窗口内的数据根据涨跌幅算净值
                let opt_changed=false;
                for (let i=0;i<chart_option.series.length;i++){{
                    if (line_other_param[i].window_cumprod_base_one && chart_option.series[i].type=="line"){{
                        opt_changed=true;
                        chart_option.series[i].data[bi][1] = 1;
                        for (let j=bi+1;j<=ei;j++){{
                            chart_option.series[i].data[j][1] = chart_option.series[i].data[j-1][1] * (1+chart_option_back.series[i].data[j][1]);
                        }}
                    }}
                }}
                if (opt_changed==true){{
                    delete chart_option.dataZoom[0].start;
                    delete chart_option.dataZoom[0].end;
                    chart_option.dataZoom[0].startValue=bi;
                    chart_option.dataZoom[0].endValue=ei;
                    chart_ins.setOption(chart_option);
                }}
                //显示当前结束点的数据
                {view_data_js if right_data_view else ""}
                let d_width=dataZoom_endValue_i-dataZoom_startValue_i+1;
                if (typeof set_ext_data_div === 'function'){{
                    set_ext_data_div(document.getElementById("ext_data_div"),ei,d_width);
                }}
                document.getElementById('date_win_width').value=d_width;                
            }});
            //时间窗口宽度设置
            let date_win_width_set = document.getElementById('date_win_width_set');
            date_win_width_set.addEventListener('click', function() {{
                let ibe={{begin:dataZoom_startValue_i,end:dataZoom_endValue_i}};
                let d_width = document.getElementById('date_win_width').value-1;
                ibe.begin = (ibe.end-d_width)>0?(ibe.end-d_width):0; 
                chart_ins.dispatchAction({{
                    type: 'dataZoom',
                    startValue: chart_option.xAxis[0].data[ibe.begin],
                    endValue: chart_option.xAxis[0].data[ibe.end],
                }});
            }});            
            //自动回放
            let auto_play = document.getElementById('auto_play');
            let is_run_play=false;
            auto_play.addEventListener('click', function() {{
                if (!is_run_play){{
                    auto_play.innerText="停止";
                    is_run_play=true;
                    do_next();
                }}else{{
                    auto_play.innerText="自动回放";
                    is_run_play=false;
                }}
                function do_next(){{
                    if (is_run_play){{
                        if (chart_option.xAxis[0].data.length-1>dataZoom_endValue_i+1){{
                            let ibe={{begin:dataZoom_startValue_i,end:dataZoom_endValue_i}};
                            ibe=play_ibe(ibe,true);
                            chart_ins.dispatchAction({{
                                type: 'dataZoom',
                                startValue: chart_option.xAxis[0].data[ibe.begin],
                                endValue: chart_option.xAxis[0].data[ibe.end],
                            }});
                        }}else{{
                            setInf("已经前进到最后一天",2000);
                            auto_play.innerText="自动回放";
                            return;
                        }}
                        let space=2000;
                        if (typeof auto_play_space === 'function'){{
                            space=auto_play_space(dataZoom_endValue_i);
                        }}
                        setTimeout(do_next, space); // 1000 毫秒后再次执行自己
                    }}
                }}
            }});
            //向前跳转
            let to_front = document.getElementById('to_front');
            to_front.addEventListener('click', function() {{
                if (chart_option.xAxis[0].data.length-1>dataZoom_endValue_i+1){{
                    let ibe={{begin:dataZoom_startValue_i,end:dataZoom_endValue_i}};
                    ibe=play_ibe(ibe,true);
                    chart_ins.dispatchAction({{
                        type: 'dataZoom',
                        startValue: chart_option.xAxis[0].data[ibe.begin],
                        endValue: chart_option.xAxis[0].data[ibe.end],
                    }});
                }}else{{
                    setInf("已经前进到最后一天",2000);
                }}
                
            }});
            // 向后跳转
            let to_back = document.getElementById('to_back');
            to_back.addEventListener('click', function() {{
                if (dataZoom_endValue_i-1>=10){{
                    let ibe={{begin:dataZoom_startValue_i,end:dataZoom_endValue_i}};
                    ibe=play_ibe(ibe,false);
                    chart_ins.dispatchAction({{
                        type: 'dataZoom',
                        startValue: chart_option.xAxis[0].data[ibe.begin],
                        endValue: chart_option.xAxis[0].data[ibe.end],
                    }});
                }}else{{
                    setInf("已经回退到第一天",2000);
                }}
            }});
            // 日期输入框跳转
            let jump_bt = document.getElementById('jump_bt');
            jump_bt.addEventListener('click', function() {{
                let dateInput = document.getElementById('date-input');
                endDate=dateInput.value;
                if (endDate.indexOf("-")<0 && endDate.length>=6){{
                    endDate = endDate.replace(/^(\\d{4})(\\d{2})(\\d{2})$/, '$1-$2-$3');

                }}
                to_date(endDate);
            }});
            
            function to_date(endDate){{
                //设置chart的dataZoom实现X轴变化
                //从后向前第一个小于等于该日期的日期/或者X轴中的一个日期,修正endDate,因为有可能用户输入的日期在X轴中不存在,或者大于X轴的最大值,或者小于X轴的最小值
                let endDate_i=-1;
                for (let i=0;i<chart_option.xAxis[0].data.length;i++){{
                    if (chart_option.xAxis[0].data[i]>=endDate){{
                        endDate=chart_option.xAxis[0].data[i]
                        endDate_i=i;
                        break;
                    }}
                }}
                let space = dataZoom_endValue_i-dataZoom_startValue_i;
                let ibe={{end:endDate_i}};
                ibe.begin=ibe.end-space>=0?ibe.end-space:0;
                ibe=play_ibe(ibe,null);
                chart_ins.dispatchAction({{
                    type: 'dataZoom',
                    startValue: chart_option.xAxis[0].data[ibe.begin],
                    endValue: chart_option.xAxis[0].data[ibe.end],
                }});   
            }}
            //默认跳到最后,并显示zoom_space个点的数据
            let d_l=chart_option.xAxis[0].data.length-1;
            let zoom_end={-1 if zoom_end is None else zoom_end};
            d_l = zoom_end>0?zoom_end:d_l;
            d_endValue=chart_option.xAxis[0].data[d_l];
            let d_startValue=chart_option.xAxis[0].data[d_l>{zoom_space}?d_l-{zoom_space}+1:0];
            chart_ins.dispatchAction({{
                type: 'dataZoom',
                startValue: d_startValue,
                endValue: d_endValue,
            }});
            // 监听点击事件,实现点击曲线隐藏该曲线
            chart_ins.on('click', (params) => {{
              if (params.seriesType === 'line') {{
                let seriesName = params.seriesName;
                chart_ins.dispatchAction({{
                    type: 'legendUnSelect',
                    name: seriesName,
                }});
              }}
            }});
    """
    # 如果高度是用%设置的,要监听浏览器窗口大小变化事件实现图表自动变大小
    if height_type == "%":
        resize_js = r"""
            function resize_chart(){{
                // 获取当前窗口的宽度和高度
                let width = window.innerWidth;
                let height = window.innerHeight;
    
                // 将 id 为 "a" 的 div 大小设置为与页面一样
                //cc[0].style.width = width + 'px';
                cc[0].style.height = height + 'px';
                chart_ins.resize();                  
            }}
            // 监听窗口大小变化事件
            window.addEventListener('resize', function () {{
                resize_chart();
            }});
            resize_chart();    
        """
        js_code += resize_js
    js_code += "</script>"
    return js_code


def _set_other_chart(chart, cur_top, chart_count, i, pic_width, height_type):
    """
    设置其它图表的各种参数
    :param chart: 图表
    :param cur_top: 当前空白区域最上面的纵坐标
    :param chart_count: 总计图表数,主要用在生成第一个图表时配置项中的多表联动部分需要知道一共有多少个图表
    :param i: 当前是第几个图表
    """
    if height_type == "%":
        legend_top = f"{cur_top}%"
    else:
        legend_top = cur_top

    # v_m = None
    # if data_item["draw_type"]=="Line":
    #     v_m = opts.VisualMapOpts(
    #         is_piecewise=True,  # 设置为分段型
    #         is_show=False,
    #         dimension=0,
    #         # series_index=i,
    #         pieces=[
    #             {"lte": 10*i, "color": "#FF0000"},  # 定义分段区间及对应颜色
    #             {"gt": 10*i, "lte": 40*i, "color": "#00FF00"},
    #             {"gt": 40*i, "color": "#0000FF"},
    #         ],
    #     )

    chart.set_global_opts(
        tooltip_opts=opts.TooltipOpts(
            trigger="axis", axis_pointer_type="cross"
        ),  # 设置鼠标悬停提示
        legend_opts=opts.LegendOpts(
            orient="vertical",
            pos_left=f"{45}",
            pos_top=legend_top,
            # is_show=True, pos_top=25, pos_left="center"
        ),
        # visualmap_opts=v_m,
        yaxis_opts=opts.AxisOpts(
            is_scale=True,
            position="right",
            splitarea_opts=opts.SplitAreaOpts(
                is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
            ),
        ),
        xaxis_opts=opts.AxisOpts(
            axislabel_opts=opts.LabelOpts(
                is_show=(i == chart_count - 1)
            )  # 设置 interval 为 None,表示不显示轴下标
        ),
    )


def _set_first_chart(
    chart, title, cur_top, chart_count, i, pic_width, height_type
) -> None:
    """
    给第一个图表设置各种参数,实现多个图表的联动显示
    :param chart: 图表
    :param title: 标题
    :param cur_top: 当前空白区域最上面的纵坐标
    :param chart_count: 总计图表数,主要用在生成第一个图表时配置项中的多表联动部分需要知道一共有多少个图表
    :param i: 当前是第几个图表
    """
    # res += '<span style="display:inline-block;margin-right:4px;border-radius:10px;width:10px;height:10px;background-color:' + params[i].color + ';"></span>';
    # 格式化提示框内容的函数
    legend_top = top_height
    tooltip_opts = opts.TooltipOpts(  # 鼠标在图表中移动时显示所有图表的当前值
        trigger="axis",
        axis_pointer_type="cross",
        background_color="rgba(245, 245, 245, 0.8)",
        border_width=1,
        border_color="#ccc",
        textstyle_opts=opts.TextStyleOpts(color="#000", font_size=13),
        # position=[20, 20],
        # formatter=JsCode(js_code_str),
    )

    chart.set_global_opts(
        title_opts=opts.TitleOpts(is_show=False),
        # 在整个图表的最上面的中间显示title
        legend_opts=opts.LegendOpts(  # 在左侧显示当前图表的数据图例
            orient="vertical",
            pos_left=f"{45}",
            # pos_right="10%",
            pos_top=legend_top,
            # align="left",
            # is_show=True, pos_top=25, pos_left="center"
        ),
        tooltip_opts=tooltip_opts,
        toolbox_opts=opts.ToolboxOpts(
            orient="vertical",
            pos_left="left",
            pos_top="43",
        ),  # 显示工具箱
        datazoom_opts=[  # 所有图表共用同一个data_zoom
            opts.DataZoomOpts(
                is_show=True,
                xaxis_index=list(range(0, chart_count)),
                type_="slider",
                pos_bottom="15",
                # pos_top="95%",
                range_start=80,
                range_end=100,
            ),
        ],
        yaxis_opts=opts.AxisOpts(
            is_scale=True,
            position="right",
            splitarea_opts=opts.SplitAreaOpts(
                is_show=True, areastyle_opts=opts.AreaStyleOpts(opacity=1)
            ),
        ),
        # visualmap_opts=opts.VisualMapOpts(
        #     is_show=False,
        #     dimension=2,
        #     series_index=5,
        #     is_piecewise=True,
        #     pieces=[
        #         {"value": 1, "color": "#00da3c"},
        #         {"value": -1, "color": "#ec0000"},
        #     ],
        # ),
        axispointer_opts=opts.AxisPointerOpts(
            is_show=True,
            link=[{"xAxisIndex": "all"}],
            label=opts.LabelOpts(background_color="#777"),
        ),
        brush_opts=opts.BrushOpts(
            x_axis_index="all",
            brush_link="all",
            out_of_brush={"colorAlpha": 0.1},
            brush_type="lineX",
        ),
        xaxis_opts=opts.AxisOpts(
            axislabel_opts=opts.LabelOpts(
                is_show=(i == chart_count - 1)
            )  # 设置 interval 为 None,表示不显示轴下标
        ),
    )


def produce_split_color_js(df, data_item, ii):
    """
    生成当前图表的分段显示不同颜色的脚本,这个本来是通过pyecharts实现的,但是发现有多个曲线要不段颜色显示时pyecharts有bug,改成直接操作echarts的operation参数实现
    :params df:图表数据所在的df
    :params data_item: 图表配置项
    :params ii: 算上子图表在内当前是第几个图表
    """
    # "split_color_col": 不必填,默认为None。轮动资金曲线或净值曲线需要根据不同的子策略分段显示不同的颜色时使用,本属性表示用df中的哪个列判断子策略。上面是业务角度的描述,通用的描述就是曲线需要根据df中的某列显示不同的颜色场景。
    # "split_color": 不必填,默认为None,但是如果split_color_col有值,则本参数一定要配置。当split_color_col有值时,可以配置本属性,用来描述每个子策略对应的颜色
    js = ""
    if "split_color_col" in data_item:
        split_color_col = data_item["split_color_col"]
        # 使用 groupby() 和 cumcount() 函数来计算连续区间
        df["group"] = (
            df[split_color_col] != df[split_color_col].shift()
        ).cumsum()  # 生成一个分组标识符
        result = (
            df.groupby([split_color_col, "group"])
            .apply(lambda x: (x[split_color_col].iloc[0], x.index[0], x.index[-1]))
            .tolist()
        )
        # 输出结果
        pieces = ""
        i = 0
        for item in result:
            # print(f"连续区间：{item[0]},起始行：{item[1]},结束行：{item[2]}")
            if item[0].strip() in data_item["split_color"]:
                pieces += f"""
                {{
                    "gte": {item[1]},
                    "lte": {item[2] + 1},
                    "color": "{data_item["split_color"][item[0].strip()]}"
                }},
            """
            i += 1
        js = f"""
            {{
                "show": false,
                "type": "piecewise",
                "dimension": 0,
                "seriesIndex": {ii},
                "pieces": [
                    {pieces}
                ]
            }},  
        """
    return js


def _produce_mark_point(
    df: pd.DataFrame, date_col: str, draw_df: pd.DataFrame, data_item, ii, time_data
):
    """
    :params buy_sale_single: 不必填,默认为None,买入卖出信号列,如果该属性配置了,则图上会根据该列的值如果为1显示做多,如果为-1显示做空,0表示平仓
    """
    js = ""
    if "trade_single" in data_item:
        js = f"""
        chart_option.series[{ii}].markPoint={{
            data:[
        """
        trade_single = data_item["trade_single"]
        draw_df["row_number"] = draw_df.reset_index().index
        draw_df = draw_df[(draw_df[trade_single].notnull())]
        for index, row in draw_df.iterrows():
            idx = row["row_number"]
            dt_df_row = df.iloc[idx]
            dt_date = time_data[idx]
            # 计算Y轴坐标。如果是曲线,直接取值。如果是K线,取最高值
            if data_item["draw_type"] == "Kline":
                dt_data = row[data_item["col"][3]]
            else:
                dt_data = row[data_item["col"]]
            z = (
                "多"
                if row[trade_single] == 1
                else ("空" if row[trade_single] == -1 else "平")
            )
            color = (
                "red"
                if row[trade_single] == 1
                else ("green" if row[trade_single] == -1 else "yellow")
            )
            js += f"""
                {{
                    coord:['{dt_date}',{dt_data}],
                    label:{{
                        position: 'bottom',
                        verticalAlign: 'bottom',
                        lineHeight: 56,
                        normal: {{
                            formatter: function (param) {{ return '{z}';}}
                        }}
                    }},
                    symbol:'path://M 10,20 L 0,10 L 20,10 Z',
                    symbolSize: 20,
                    symbolOffset:[0, '-50%'],
                    itemStyle: {{
                        normal: {{color: '{color}'}}
                    }}
                }},
            """
        js += """
            ]
        };
        """
    return js


def _produce_tooltip_formatter():
    js_code_str = """
        chart_option.tooltip.formatter = function(params) {
            let res = params[0].axisValue;
            for (let i = 0; i < params.length; i++) {
                // 判断 line_other_param[i] 是否存在以及 dec_length 是否存在
                let dec_length = (line_other_param[i] && line_other_param[i].dec_length) || 2; // 默认值为 2
                res += '<div>';
                res += params[i].marker;

                if (params[i].seriesType === 'line') {
                    res += params[i].seriesName + '：' + fixDecLen(params[i].value[1], dec_length);
                } else if (params[i].seriesType === 'candlestick') {
                    let zdf = params[i].value[2] / params[i].value[1] - 1;
                    zdf = (zdf * 100).toFixed(2);
                    res += params[i].seriesName + '：开(' + fixDecLen(params[i].value[1], dec_length) + '), 收('
                        + fixDecLen(params[i].value[2], dec_length) + '), 低('
                        + fixDecLen(params[i].value[3], dec_length) + '), 高('
                        + fixDecLen(params[i].value[4], dec_length) + '), 涨(<span style="color:' + (zdf > 0 ? 'red' : 'green') + ';">'
                        + zdf + '%</span>)';
                } else {
                    res += params[i].seriesName + '：' + fixDecLen(params[i].value, dec_length);
                }
                res += '</div>';
            }
            return res;
        }
    """
    return js_code_str
