<template>
    <div id="sunburst-container" :style="{width:600,height:600}">
    </div>
</template>
<script>
    import * as d3 from 'd3';


    export default {
        name: 'Sunburst',
        props: ['options'],
        data() {
            return {
                sunburst: null,
                g: null,
                chart: null,
                title: null,
                titleText: 'Sunburst',
                titleRectWidth: 460,
                titleRectHeight: 40,
                width: 460,
                height: 460,
                chartPadding: {top: 80, right: 80, bottom: 80, left: 80},
                data: [],
                root: null, // 层级数据根
            };
        },
        // https://cn.vuejs.org/v2/api/#mounted
        mounted() {
            // 这里会在实例被挂载后调用
            // 初始化图表
            this.initSunburst();
            this.readData();
            this.render();
        },
        // https://cn.vuejs.org/v2/api/#computed
        // https://cn.vuejs.org/v2/guide/computed.html#%E5%9F%BA%E7%A1%80%E4%BE%8B%E5%AD%90
        computed: {
            // 这里是一些计算属性，当其中涉及的值发生变化时，计算属性会重新计算，返回新的值
            ascendingData() {
                // 升序排序
                return this.sortKeyAscending(this.originData, 'value');
            },
            descendingData() {
                // 降序排序
                return this.sortKeyDescending(this.originData, 'value');
            }
        },
        // https://cn.vuejs.org/v2/api/#watch
        watch: {
            // watch的作用可以监控一个值的变换，并调用因为变化需要执行的方法。可以通过watch动态改变关联的状态。
            // 这里是一些可被修改的配置项，例如图表标题内容、标题是否显示等
            'options.titleText': {
                handler() {
                    this.titleText = this.options.titleText;
                    this.title.select('text').text(this.titleText);
                }
            },
            'options.titleIsShow': {
                handler() {
                    if (this.options.titleIsShow) {
                        this.title.attr('style', 'display: block');
                    } else {
                        this.title.attr('style', 'display: none');
                    }
                }
            },
            // 请根据组件需要补充...
        },
        // https://cn.vuejs.org/v2/api/#methods
        methods: {
            // 这里是一些组件其余地方会使用到的函数，调用方式为 this.xxxx()
            // 例如mounted中的图表初始化函数 initSunburst() 就应该被定义在这里
            // 其余与交互、更新有关的函数也都写在这里
            initSunburst() {
                // 在这里编写初始化图表的代码，以下代码仅供参考，均可调整
                // 可以使用d3绘制可视化图表，具体可参考 bar chart 示例和 README.md 中的链接
                console.log(this.options);

                // 指定图表的宽高
                this.width = 700 - this.chartPadding.right - this.chartPadding.left - 180;
                this.height = 700 - this.chartPadding.bottom - this.chartPadding.top - 80;

                d3.select('#sunburst-container')
                    .style('width', '720px')
                    .style('height', '720px');

                // 添加svg
                this.svg = d3.select('#sunburst-container').append('svg')
                    .attr('style', 'background: #eee')
                    .attr('width', 700)
                    .attr('height', 700);
                // 添加g标签
                this.g = this.svg.append('g')
                    .attr('class', 'chart')  // 图表部分
                    .attr('transform', `translate(${this.chartPadding.left + 40}, ${this.chartPadding.top + 40})`);
                // 添加图表标题
                this.title = this.svg.append('g')
                    .attr('transform', 'translate(0,0)')
                    .attr('style', 'display: none');     // 默认不显示
                // 标题背景框
                this.title.append('rect')
                    .attr('class', 'title')
                    .attr('width', 700)
                    .attr('height', `${this.titleRectHeight}`)
                    .attr('fill', '#E3E3E3')
                    .attr('x', '0')
                    .attr('y', '0');
                // 标题文本
                this.title.append('text')
                    .text(this.titleText)
                    .attr('x', 350)
                    .attr('y', 25)
                    .attr('text-anchor', 'middle')
                    .attr('fill', '#000');

            },

            // 读入并格式化数据
            readData() {
                d3.json('games.json').then(data => {
                    this.root = d3.partition().size([2 * Math.PI, this.height / 1.6])(
                        d3.hierarchy(data)
                            .sum(d => d.popularity)
                            .sort((a, b) => b.popularity - a.popularity));
                });
            },

            // 绘制Sunburst
            render() {
                const arc = d3.arc() // 指定path的d属性，用于绘制扇环
                    .startAngle(d => d.x0) // 弧度制
                    .endAngle(d => d.x1)
                    .innerRadius(d => d.y0)
                    .outerRadius(d => d.y1)
                    .padAngle(0.2 / 180 * Math.PI)
                    .padRadius(0.1);

                const color = d3.scaleOrdinal() // 序数比例尺，用于domain和range均为离散的情况
                    .domain(this.root.descendants().filter(d => d.depth <= 1).map(d => d.data.name))
                    .range(d3.schemeCategory10); // d3默认的一个配色方案

                const fill = d => { // 用于返回扇环的颜色
                    if (d.depth === 0)
                        return color(d.data.name);
                    let node = d;
                    while (node.depth > 1)
                        node = node.parent;
                    return color(node.data.name);
                };

                this.g.selectAll('.dataPath')
                    .data(this.root.descendants().filter(d => d.depth !== 0))
                    .join('path')
                    .attr('class', 'dataPath')
                    .attr('d', arc)
                    .attr('fill', fill);

                this.g.selectAll('.dataText')
                    .data(this.root.descendants().filter(d => d.depth !== 0))
                    .join('text')
                    .attr('class', 'dataText')
                    .text(d => d.data.name)
                    .attr('text-anchor', 'middle')
                    .attr('transform', d => {
                        let angle = (d.x0 + d.x1) / 2;
                        const displacement = (d.y0 + d.y1) / 2;
                        angle = angle < 180 ? angle + 1 : angle - 1; // 角度微调，确保文本居中
                        // rotate中0°是竖直的，因而需要减去90°
                        return `rotate(${angle - 90} translate(${displacement}, ${0}) rotate(${angle < 180 ? 0 : 180}))`;
                    }); // todo 调整字体大小

            },
        }

    };
</script>
<style scoped>
    text {
        background: '#000';
    }

    #sunburst-container {
        overflow: hidden;
    }
</style>