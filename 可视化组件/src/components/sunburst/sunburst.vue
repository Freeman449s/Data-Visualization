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
                titleRectHeight: 60,
                titleRectX: 180,
                titleRectY: 25,
                titleBackground: '#E3E3E3',
                titleFontSize: 16,
                titleFontFamily: 'Arial',
                titleFontColor: '#000',
                titleTextElem: null,
                titleRectElem: null,
                width: 460,
                height: 460,
                chartPadding: {top: 300, right: 300, bottom: 300, left: 300},
                data: [],
                root: null, // 层级数据根
                svgWidth: 1080,
                svgHeight: 720,
                legend: null,
                showLegend: false,
            };
        },
        // https://cn.vuejs.org/v2/api/#mounted
        mounted() {
            // 这里会在实例被挂载后调用
            // 初始化图表
            this.initSunburst();
            this.readAndRender();
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
            'options.titleBackground': {
                handler() {
                    this.titleBackground = this.options.titleBackground;
                    this.title.select('rect').attr('fill', this.titleBackground);
                }
            },
            'options.titleFontSize': {
                handler() {
                    this.titleFontSize = this.options.titleFontSize;
                    this.titleTextElem.attr('font-size', `${this.titleFontSize}px`);
                }
            },
            'options.titleFontFamily': {
                handler() {
                    this.titleFontFamily = this.options.titleFontFamily;
                    this.titleTextElem.attr('font-family', this.titleFontFamily);
                }
            },
            'options.titleFontColor': {
                handler() {
                    this.titleFontColor = this.options.titleFontColor;
                    this.titleTextElem
                        .attr('stroke', this.titleFontColor)
                        .attr('fill', this.titleFontColor);
                }
            },
            'options.showLegend': {
                handler() {
                    this.showLegend = this.options.showLegend;
                    if (this.options.showLegend) {
                        this.legend.attr('style', 'display: block');
                    } else {
                        this.legend.attr('style', 'display: none');
                    }
                }
            }
        },
        // https://cn.vuejs.org/v2/api/#methods
        methods: {
            // 这里是一些组件其余地方会使用到的函数，调用方式为 this.xxxx()
            // 例如mounted中的图表初始化函数 initSunburst() 就应该被定义在这里
            // 其余与交互、更新有关的函数也都写在这里
            initSunburst() {
                // 在这里编写初始化图表的代码，以下代码仅供参考，均可调整
                // 可以使用d3绘制可视化图表，具体可参考 bar chart 示例和 README.md 中的链接
                // console.log(this.options);

                // 指定图表的宽高
                this.width = 1080 - this.chartPadding.right - this.chartPadding.left;
                this.height = 720 - this.chartPadding.bottom - this.chartPadding.top;

                d3.select('#sunburst-container')
                    .style('width', '1080px')
                    .style('height', '720px');

                // 添加svg
                this.svg = d3.select('#sunburst-container').append('svg')
                    .attr('style', 'background: #eee')
                    .attr('width', this.svgWidth)
                    .attr('height', this.svgHeight);
                // 添加g标签
                this.g = this.svg.append('g')
                    .attr('class', 'chart')  // 图表部分
                    .attr('transform', `translate(${this.svgWidth / 2}, ${this.svgHeight / 2})`);
                // 添加图表标题
                this.title = this.svg.append('g')
                    .attr('transform', 'translate(0,0)');
                // 标题背景框
                this.titleRectElem = this.title.append('rect')
                    .attr('class', 'title')
                    .attr('width', 720)
                    .attr('height', `${this.titleRectHeight}`)
                    .attr('fill', '#E3E3E3')
                    .attr('x', this.titleRectX)
                    .attr('y', this.titleRectY)
                    .attr('rect-anchor', 'middle');
                // 标题文本
                this.titleTextElem = this.title.append('text')
                    .text(this.titleText)
                    .attr('x', `${this.svgWidth / 2}`)
                    .attr('y', this.titleRectY + this.titleRectHeight / 2 + 8)
                    .attr('text-anchor', 'middle')
                    .attr('fill', '#000');

            },

            // 读入并格式化数据
            readAndRender() {
                // console.log('readData');
                d3.json('static/data/games.json').then(data => { // 当前目录为index所在目录
                    // console.log('then');
                    this.root = d3.partition().size([2 * Math.PI, Math.min(this.svgHeight, this.svgWidth) * 0.55])(
                        d3.hierarchy(data)
                            .sum(d => d.popularity)
                            .sort((a, b) => b.popularity - a.popularity));
                    // console.log('root');
                    // console.log(this.root);
                    this.render();
                });
            },

            // 绘制Sunburst
            render() {
                // console.log('render');
                // console.log('root');
                // console.log(this.root);

                const arc = d3.arc() // 指定path的d属性，用于绘制扇环
                    .startAngle(d => d.x0) // 弧度制
                    .endAngle(d => d.x1)
                    .innerRadius(d => d.y0 + 1)
                    .outerRadius(d => d.y1)
                    .padAngle(0.2 / 180 * Math.PI);

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
                        const angle = (d.x0 + d.x1) / 2 * 180 / Math.PI;
                        const displacement = (d.y0 + d.y1) / 2;
                        const adjustedAngle = angle < 180 ? angle + 1 : angle - 1; // 角度微调，确保文本居中
                        // rotate中0°是竖直的，因而需要减去90°
                        return `rotate(${adjustedAngle - 90}) translate(${displacement}, ${0}) rotate(${angle < 180 ? 0 : 180})`;
                    })
                    .attr('font-size', d => {
                        const size = d.data.name.length <= 10 ? 0.5 : 0.5 * 10 / d.data.name.length;
                        return `${size}em`;
                    });
                this.renderLegend();
            },

            // 绘制图例
            renderLegend() {
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

                let firstRectX = 920, firstRectY = 540; //第一个矩形的坐标
                this.legend = this.svg.append('g');

                this.legend.selectAll('.legendRect')
                    .data(this.root.descendants().filter(d => d.depth === 1))
                    .join('rect')
                    .attr('class', 'legendRect')
                    .attr('fill', fill)
                    .attr('x', firstRectX)
                    .attr('y', (d, i) => firstRectY + i * 20)
                    .attr('width', 10)
                    .attr('height', 10);

                this.legend.selectAll('.legendText')
                    .data(this.root.descendants().filter(d => d.depth === 1))
                    .join('text')
                    .attr('class', 'legendText')
                    .attr('x', firstRectX + 15)
                    .attr('y', (d, i) => firstRectY + i * 20 + 12)
                    .text(d => d.data.name);

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