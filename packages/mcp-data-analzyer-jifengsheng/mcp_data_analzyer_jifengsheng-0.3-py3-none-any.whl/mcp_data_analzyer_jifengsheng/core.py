from contextlib import AbstractAsyncContextManager
from typing import Callable

from mcp.server import Server
from mcp.server.lowlevel.server import LifespanResultT, RequestT, lifespan
from mcp.types import TextContent, Tool
import httpx
import json
import os
from pathlib import Path
from typing import List
import platform
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

if platform.system() == 'Darwin':  # macOS
    plt.rcParams['font.family'] = 'Arial Unicode MS'
elif platform.system() == 'Windows':
    plt.rcParams['font.family'] = 'Microsoft YaHei'
else:  # Linux
    plt.rcParams['font.family'] = 'SimHei'  # 或者你安装的中文字体


class DataAnalyzerServer(Server):

    def __init__(self, name: str, version: str | None = None, instructions: str | None = None, lifespan: Callable[
        [Server[LifespanResultT, RequestT]],
        AbstractAsyncContextManager[LifespanResultT],
    ] = lifespan):
        super().__init__(name, version, instructions, lifespan)
        self._amap_key = None

    @property
    def amap_key(self):
        return self._amap_key

    @amap_key.setter
    def amap_key(self, value):
        self._amap_key = value


app = DataAnalyzerServer("data-analyzer-server")
import dotenv

dotenv.load_dotenv()


def _format_number(num):
    """
    格式化数字，对于大于万的数字使用万、十万、百万等单位
    """
    try:
        num_val = float(num)  # 转换numpy数值类型为Python float
        if abs(num_val) >= 1e8:  # 亿
            return f"{num_val / 1e8:.1f}亿"
        elif abs(num_val) >= 1e4:  # 万
            return f"{num_val / 1e4:.1f}万"
        else:
            return f"{num_val:.1f}"
    except (ValueError, TypeError):
        return str(num)


def _format_yaxis(ax, max_value):
    """
    格式化y轴刻度
    """
    # 根据数据最大值确定基准单位
    if max_value >= 1e8:  # 亿
        scale = 1e8
        unit = '亿'
    elif max_value >= 1e4:  # 万
        scale = 1e4
        unit = '万'
    else:
        scale = 1
        unit = ''

    # 获取当前刻度
    yticks = ax.get_yticks()
    # 设置新的刻度标签
    ax.set_yticklabels([f'{y / scale:.1f}' for y in yticks])
    # 返回使用的单位，供修改ylabel使用
    return unit


def _get_aggfunc_chinese(aggfunc: str) -> str:
    """
    将聚合函数名称转换为中文
    """
    aggfunc_map = {
        "sum": "总和",
        "mean": "平均值",
        "count": "计数",
        "max": "最大值",
        "min": "最小值",
        "median": "中位数",
        "std": "标准差",
        "var": "方差"
    }
    return aggfunc_map.get(aggfunc.lower(), aggfunc)


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "data_overview":
        return await data_overview(arguments["data_path"])
    elif name == "data_summary":
        return await data_summary(arguments["data_path"])
    elif name == "visualize_data":
        data_path = arguments["data_path"]
        index = arguments["index"]
        values = arguments["values"]
        aggfunc = arguments.get("aggfunc", "sum")
        output_dir = arguments.get("out_dir", "./output")
        return await visualize_data(data_path, index, values, aggfunc, output_dir)
    else:
        return [TextContent(type="text", text=f"not support function call")]


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="data_overview",
            description="获取数据的大概情况，例如表头信息、表头对应的字段类型、数据条数等",
            inputSchema={
                "type": "object",
                "properties": {
                    "data_path": {
                        "type": "string",
                        "description": "数据文件的路径，支持csv|.xlsx|.xls格式"
                    }
                },
                "required": ["data_path"]
            }
        ),
        Tool(
            name="visualize_data",
            description="通过数据透视的方式可视化数据",
            inputSchema={
                "type": "object",
                "properties": {
                    "data_path": {
                        "type": "string",
                        "description": "数据文件的路径，支持csv|.xlsx|.xls格式"
                    },
                    "index": {
                        "type": "array",
                        "description": "数据透视的索引列名列表，支持1-2维度，如['城市','季度']",
                        "items": {
                            "type": "string"
                        }
                    },
                    "values": {
                        "type": "array",
                        "description": "需要聚合的数值列名列表，如['销量','销售额']",
                        "items": {
                            "type": "string"
                        }
                    },
                    "aggfunc": {
                        "type": "string",
                        "description": "聚合函数，支持 sum | mean | count | max | min | median | std | var，默认是sum",
                    },
                    "out_dir": {
                        "type": "string",
                        "description": "聚合图表的保存目录，默认./output"
                    }
                },
                "required": ["data_path"]
            }
        ),
        Tool(
            name="data_summary",
            description="获取数据的汇总分析情况，例如整体数据的平均值、中位数、方差等等",
            inputSchema={
                "type": "object",
                "properties": {
                    "data_path": {
                        "type": "string",
                        "description": "数据文件的路径，支持csv|.xlsx|.xls格式"
                    }
                },
                "required": ["data_path"]
            }
        ),
    ]


async def data_summary(data_path: str) -> list[TextContent]:
    try:
        # 读取数据
        file_ext = Path(data_path).suffix.lower()
        if file_ext == '.csv':
            df = pd.read_csv(data_path)
        elif file_ext in ['.xlsx', '.xls']:
            df = pd.read_excel(data_path)
        else:
            return [TextContent(type="text", text=f"Unsupported file format: {file_ext}")]

        # 生成基本统计信息
        summary = []
        summary.append("数据分析总结：")
        summary.append(f"1. 数据集包含 {len(df)} 行和 {len(df.columns)} 列")

        # 数值列统计
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns
        if len(numeric_cols) > 0:
            summary.append("\n2. 数值列统计：")
            for col in numeric_cols:
                stats = df[col].describe()
                summary.append(f"   - {col}:")
                summary.append(f"     平均值: {stats['mean']:.2f}")
                summary.append(f"     中位数: {stats['50%']:.2f}")
                summary.append(f"     最大值: {stats['max']:.2f}")
                summary.append(f"     最小值: {stats['min']:.2f}")

        # 类别列统计
        categorical_cols = df.select_dtypes(include=['object']).columns
        if len(categorical_cols) > 0:
            summary.append("\n3. 类别列统计：")
            for col in categorical_cols:
                value_counts = df[col].value_counts()
                summary.append(f"   - {col}:")
                summary.append(f"     唯一值数量: {len(value_counts)}")
                if len(value_counts) > 0:
                    summary.append(f"     最常见值: {value_counts.index[0]} (出现 {value_counts.iloc[0]} 次)")

        # 缺失值统计
        missing_values = df.isnull().sum()
        if missing_values.sum() > 0:
            summary.append("\n4. 缺失值统计：")
            for col, count in missing_values[missing_values > 0].items():
                summary.append(f"   - {col}: {count} 个缺失值")

        return [TextContent(type="text", text="\n".join(summary))]

    except Exception as e:
        return [TextContent(type="text", text=f"Error summarizing data: {str(e)}")]


async def data_overview(data_path: str) -> list[TextContent]:
    try:
        # 根据文件扩展名读取数据
        file_ext = Path(data_path).suffix.lower()
        if file_ext == '.csv':
            df = pd.read_csv(data_path)
        elif file_ext in ['.xlsx', '.xls']:
            df = pd.read_excel(data_path)
        else:
            return [TextContent(type="text", text=f"Unsupported file format: {file_ext}")]

        overview = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "columns": list(df.columns),
            "data_types": {str(k): str(v) for k, v in df.dtypes.to_dict().items()},
            "missing_values": df.isnull().sum().to_dict(),
            "sample_data": df.head(5).to_dict()
        }

        return [TextContent(type="text", text=json.dumps(overview, indent=2))]

    except Exception as e:
        return [TextContent(type="text", text=f"Error analyzing data: {str(e)}")]


def _decode_unicode_escape(s: str) -> str:
    """
    仅当字符串包含 Unicode 转义时才解码，否则直接返回原字符串
    """
    if ("\\u" in s) or ("\\U" in s):
        try:
            return s.encode('utf-8').decode('unicode_escape')
        except Exception:
            return s  # 解码失败时返回原字符串
    return s


async def visualize_data(
        data_path: str,
        index: List[str],
        values: List[str],
        aggfunc: str = "sum",
        output_dir: str = "./output"
) -> list[TextContent]:
    """
    通过数据透视表方式可视化数据
    Args:
        data_path: 数据文件路径，支持.xlsx和.csv格式
        index: 数据透视表的索引列名列表，支持1-2个维度，如 ["城市", "季度"]
        values: 需要聚合的数值列名列表，如 ["销售额", "利润"]
        aggfunc: 聚合函数，支持"sum"、"mean"、"count"、"max"、"min"等，默认为"sum"
        output_dir: 图表保存目录，默认为"./output"
    Returns:
        包含可视化结果信息的TextContent列表，每个图表信息包括：
        - type: 图表类型
        - path: 图表文件路径
        - data: 对应的数据（DataFrame或Series）
        - description: 图表描述
    """
    try:
        # 解码Unicode转义序列
        index = [_decode_unicode_escape(idx) for idx in index]
        values = [_decode_unicode_escape(val) for val in values]

        # 验证参数
        if len(index) > 2:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "message": "索引维度最多支持2个",
                    "plots": [],
                    "error": "TooManyIndexDimensions"
                }, ensure_ascii=False, indent=2)
            )]

        if len(values) == 0:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "message": "至少需要指定一个需要聚合的数值列",
                    "plots": [],
                    "error": "NoValuesSpecified"
                }, ensure_ascii=False, indent=2)
            )]

        # 读取数据
        file_ext = Path(data_path).suffix.lower()
        if file_ext == '.csv':
            df = pd.read_csv(data_path)
        elif file_ext in ['.xlsx', '.xls']:
            df = pd.read_excel(data_path)
        else:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "success": False,
                    "message": f"不支持的文件格式: {file_ext}",
                    "plots": [],
                    "error": "UnsupportedFileFormat"
                }, ensure_ascii=False, indent=2)
            )]

        # 创建输出目录
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        generated_plots = []

        # 获取聚合函数的中文名称
        aggfunc_cn = _get_aggfunc_chinese(aggfunc)

        # 根据索引维度数量生成不同类型的可视化
        if len(index) == 1:
            # 单维度分析
            for value in values:
                # 创建透视表
                pivot_table = pd.pivot_table(
                    df,
                    values=value,
                    index=index[0],
                    aggfunc=aggfunc
                )

                # 柱状图
                plt.figure(figsize=(12, 6))
                ax = pivot_table.plot(kind='bar')
                plt.title(f"{index[0]}维度下{value}的{aggfunc_cn}")
                plt.xlabel(index[0])

                # 格式化y轴
                unit = _format_yaxis(ax, pivot_table.values.max())
                plt.ylabel(f"{value}({aggfunc_cn}){f'({unit})' if unit else ''}")

                plt.xticks(rotation=45)

                # 添加数值标签
                for i, v in enumerate(pivot_table.values):
                    ax.text(i, v, _format_number(v), ha='center', va='bottom')

                plt.tight_layout()
                plot_path = f"{output_dir}/bar_{index[0]}_{value}_{aggfunc}.png"
                plt.savefig(plot_path, bbox_inches='tight', dpi=300)
                plt.close()

                generated_plots.append({
                    "type": "bar",
                    "path": plot_path,
                    "data": pivot_table.to_dict(),
                    "description": f"{index[0]}维度下{value}的{aggfunc_cn}柱状图"
                })

                # 饼图（仅当聚合值为正时）
                pivot_values = pivot_table.values.flatten()
                if len(pivot_values) > 0 and (pivot_values > 0).all():
                    plt.figure(figsize=(10, 8))
                    plt.pie(pivot_values, labels=[f"{idx}\n({_format_number(val)})" for idx, val in
                                                  zip(pivot_table.index, pivot_values)], autopct='%1.1f%%')
                    plt.title(f"{index[0]}维度下{value}的{aggfunc_cn}占比")
                    plot_path = f"{output_dir}/pie_{index[0]}_{value}_{aggfunc}.png"
                    plt.savefig(plot_path, bbox_inches='tight', dpi=300)
                    plt.close()

                    generated_plots.append({
                        "type": "pie",
                        "path": plot_path,
                        "data": pivot_table.to_dict(),
                        "description": f"{index[0]}维度下{value}的{aggfunc_cn}占比图"
                    })

        elif len(index) == 2:
            # 双维度分析
            for value in values:
                # 创建透视表
                pivot_table = pd.pivot_table(
                    df,
                    values=value,
                    index=index[0],
                    columns=index[1],
                    aggfunc=aggfunc,
                    fill_value=0
                )

                # 热力图
                plt.figure(figsize=(12, 8))
                sns.heatmap(pivot_table, annot=True, fmt='.2f', cmap='YlOrRd')
                # 获取热力图的注释文本对象
                annot = [text for text in plt.gca().texts]
                # 更新注释文本
                for i, text in enumerate(annot):
                    value = pivot_table.values.flatten()[i]
                    text.set_text(_format_number(value))
                plt.title(f"{index[0]}和{index[1]}维度下{value}的{aggfunc_cn}热力图")
                plot_path = f"{output_dir}/heatmap_{index[0]}_{index[1]}_{value}_{aggfunc}.png"
                plt.savefig(plot_path, bbox_inches='tight', dpi=300)
                plt.close()

                generated_plots.append({
                    "type": "heatmap",
                    "path": plot_path,
                    "data": pivot_table.to_dict(),
                    "description": f"{index[0]}和{index[1]}维度下{value}的{aggfunc_cn}热力图"
                })

                # 堆叠柱状图
                plt.figure(figsize=(12, 6))
                ax = pivot_table.plot(kind='bar', stacked=True)
                plt.title(f"{index[0]}和{index[1]}维度下{value}的{aggfunc_cn}堆叠分析")
                plt.xlabel(index[0])

                # 格式化y轴
                unit = _format_yaxis(ax, pivot_table.values.sum(axis=1).max())
                plt.ylabel(f"{value}({aggfunc_cn}){f'({unit})' if unit else ''}")

                plt.legend(title=index[1], bbox_to_anchor=(1.05, 1), loc='upper left')

                # 添加数值标签
                for j, c in enumerate(pivot_table.columns):
                    for i, v in enumerate(pivot_table[c]):
                        if v > 0:  # 只显示正值
                            ax.text(i, pivot_table.iloc[i, :j].sum() + v / 2, _format_number(v), ha='center',
                                    va='center')

                plt.tight_layout()
                plot_path = f"{output_dir}/stacked_bar_{index[0]}_{index[1]}_{value}_{aggfunc}.png"
                plt.savefig(plot_path, bbox_inches='tight', dpi=300)
                plt.close()

                generated_plots.append({
                    "type": "stacked_bar",
                    "path": plot_path,
                    "data": pivot_table.to_dict(),
                    "description": f"{index[0]}和{index[1]}维度下{value}的{aggfunc_cn}堆叠柱状图"
                })

                # 分组柱状图
                plt.figure(figsize=(12, 6))
                ax = pivot_table.plot(kind='bar')
                plt.title(f"{index[0]}和{index[1]}维度下{value}的{aggfunc_cn}分组分析")
                plt.xlabel(index[0])

                # 格式化y轴
                unit = _format_yaxis(ax, pivot_table.values.max())
                plt.ylabel(f"{value}({aggfunc_cn}){f'({unit})' if unit else ''}")

                plt.legend(title=index[1], bbox_to_anchor=(1.05, 1), loc='upper left')

                # 添加数值标签
                for i in range(len(pivot_table.index)):
                    for j, col in enumerate(pivot_table.columns):
                        v = pivot_table.iloc[i, j]
                        ax.text(i, v, _format_number(v), ha='center', va='bottom')

                plt.tight_layout()
                plot_path = f"{output_dir}/grouped_bar_{index[0]}_{index[1]}_{value}_{aggfunc}.png"
                plt.savefig(plot_path, bbox_inches='tight', dpi=300)
                plt.close()

                generated_plots.append({
                    "type": "grouped_bar",
                    "path": plot_path,
                    "data": pivot_table.to_dict(),
                    "description": f"{index[0]}和{index[1]}维度下{value}的{aggfunc_cn}分组柱状图"
                })

        # 如果有多个values，生成对比分析图
        if len(values) > 1:
            # 创建多值透视表
            multi_pivot = pd.pivot_table(
                df,
                values=values,
                index=index,
                aggfunc=aggfunc
            )

            # 多值对比柱状图
            plt.figure(figsize=(12, 6))
            ax = multi_pivot.plot(kind='bar')
            plt.title(f"{'+'.join(index)}维度下{'+'.join(values)}的{aggfunc_cn}对比")
            plt.xlabel('+'.join(index))

            # 格式化y轴
            unit = _format_yaxis(ax, multi_pivot.values.max())
            plt.ylabel(f"值({aggfunc_cn}){f'({unit})' if unit else ''}")

            plt.legend(title='指标', bbox_to_anchor=(1.05, 1), loc='upper left')

            # 添加数值标签
            for i in range(len(multi_pivot.index)):
                for j, col in enumerate(multi_pivot.columns):
                    v = multi_pivot.iloc[i, j]
                    ax.text(i, v, _format_number(v), ha='center', va='bottom')

            plt.tight_layout()
            plot_path = f"{output_dir}/multi_value_comparison_{aggfunc}.png"
            plt.savefig(plot_path, bbox_inches='tight', dpi=300)
            plt.close()

            # Convert multi_pivot to a dictionary format that can be serialized
            multi_pivot_dict = {
                'index': multi_pivot.index.tolist(),
                'columns': multi_pivot.columns.tolist(),
                'data': multi_pivot.values.tolist()
            }

            generated_plots.append({
                "type": "multi_value_comparison",
                "path": plot_path,
                "data": multi_pivot_dict,
                "description": f"{'+'.join(index)}维度下{'+'.join(values)}的{aggfunc_cn}对比图"
            })

        return [TextContent(
            type="text",
            text=json.dumps({
                "success": True,
                "message": f"成功生成 {len(generated_plots)} 个图表",
                "plots": generated_plots,
                "error": None
            }, ensure_ascii=False, indent=2)
        )]

    except Exception as e:
        return [TextContent(
            type="text",
            text=json.dumps({
                "success": False,
                "message": f"生成图表时发生错误: {str(e)}",
                "plots": [],
                "error": str(e)
            }, ensure_ascii=False, indent=2)
        )]


async def serve():
    from mcp.server.stdio import stdio_server
    async def arun():
        async with stdio_server() as streams:
            await app.run(streams[0], streams[1], app.create_initialization_options())
    await arun();



