let svg = d3.select('#mainSvg');
let width = svg.attr('width'), height = svg.attr('height');
let nodes, links;
let circles, lines;
let color;
let simulation;
let infoGroup, infoBox;
const boxWidth = 640, boxHeight = 165;
let selectedColor = "#EE0000", defaultColor = "#0000EE", connectedColor = "#EE0099";

/**
 * 渲染初始化
 */
const renderInit = function () {
    const computeR = d3.scaleLinear()
        .domain([d3.min(nodes, d => d.nConnections), d3.max(nodes, d => d.nConnections)])
        .range([5, 20]);

    svg.append("text")
        .text("PythonExp")
        .attr("text-anchor", "middle")
        .attr("x", width / 2)
        .attr("y", 100)
        .attr("font-size", "3em");

    lines = svg.selectAll("line").data(links).join("line")
        .attr("stroke", "black")
        .attr("opacity", 0.8)
        .attr("stroke-width", 0.5); //仅设置外观，位置在ticked函数内设置

    circles = svg.selectAll("circle").data(nodes).join("circle")
        .attr("r", function (d) {
            return computeR(d.nConnections);
        })
        .attr("fill", "blue")
        .call(onDrag) //响应拖拽事件
        .on("mouseover", function (d) { //响应悬浮事件
            tip.show(d);
        })
        .on("mouseout", function (d) {
            tip.hide(d);
        })
        .on("click", function (d) {
            console.log("click", d);
            d3.selectAll("circle")
                .transition()
                .duration(300)
                .attr("fill", defaultColor);
            d3.select(this)
                .transition()
                .duration(300)
                .attr("fill", selectedColor);
            paintConnected(d, connectedColor);
            refreshInfoBox(d);
            boxPopOut();
        });

    infoGroup = svg.append("g") //信息提示窗口
        .attr("id", "infoG")
        .attr("transform", `translate(${width},50)`);
    infoBox = infoGroup.append("rect")
        .attr("id", "infoBox")
        .attr("color", "black")
        .attr("width", boxWidth)
        .attr("height", boxHeight)
        .attr("opacity", 0.8);
};

/**
 * 标签显示函数
 */
const tip = d3.tip()
    .attr("class", "d3-tip")
    .html(d => d.name);
svg.call(tip);


/**
 * 定义拖动事件响应函数
 * @type {*|undefined|f|d|g}
 */
const onDrag = d3.drag()
    .on("start", function (d) {
        console.log("dragStart", d);
        d3.selectAll("circle") //所有圆形恢复蓝色
            .transition()
            .duration(300)
            .attr("fill", defaultColor);
        d3.select(this)
            .raise()
            .transition()
            .duration(300)
            .attr("fill", selectedColor)
            .attr("stroke", "black")
            .attr("stroke-width", 3);
        simulation
            .alphaTarget(0.3)
            .restart(); //重新启动模拟
        paintConnected(d, connectedColor);
        refreshInfoBox(d);
        boxPopOut();
    })
    .on("drag", function (d) {
        d3.select(this)
            .attr("cx", d.x = d3.event.x)
            .attr("cy", d.y = d3.event.y);
        ticked();
    })
    .on("end", function (d) {
        d3.select(this)
            .transition()
            .duration(300)
            .attr("fill", defaultColor)
            .attr("stroke", null);
        simulation.alphaTarget(0);
        paintConnected(d, defaultColor);
        boxHide();
    });


/**
 * 更新图元位置
 */
const ticked = function () {
    lines
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

    circles
        .attr("cx", d => d.x)
        .attr("cy", d => d.y);
};

/**
 * 返回模块d所导入的模块，或导入模块d的模块的名称组成的字符串
 */
function import_str(d, list, type) {
    let str;
    if (type === "imports") str = "Imports: ";
    else str = "Imported By: ";
    //列表为空
    if (list.length === 0) {
        str += "None";
        return str;
    }
    //列表非空
    let bound = Math.min(3, list.length);
    for (let i = 0; i <= bound - 1; i++) {
        str += list[i].name;
        if (i + 1 < bound) {
            str += ", ";
        }
    }
    if (list.length > 3) {
        str += ", etc.";
    }
    str += " (total " + list.length + ")";
    return str;
}

/**
 * 刷新信息提示框
 */
function refreshInfoBox(d) {
    //添加文本
    infoGroup.selectAll("text")
        .remove();
    infoGroup.append("text")
        .text(d.name)
        .attr("fill", "#E3E3E3")
        .attr("font-size", "1.5em")
        .attr("transform", "translate(20,40)");
    infoGroup.append("text")
        .text("nLines: " + (d.nLines > 0 ? d.nLines : "No statistics"))
        .attr("fill", "#E3E3E3")
        .attr("font-size", "1.5em")
        .attr("transform", `translate(20,${40 + 32})`);
    infoGroup.append("text")
        .text(import_str(d, d.imports, "imports"))
        .attr("fill", "#E3E3E3")
        .attr("font-size", "1.5em")
        .attr("transform", `translate(20,${40 + 32 * 2})`);
    infoGroup.append("text")
        .text(import_str(d, d.importedBy, "imported by"))
        .attr("fill", "#E3E3E3")
        .attr("font-size", "1.5em")
        .attr("transform", `translate(20,${40 + 32 * 3})`);
}

/**
 * 信息提示框弹出
 */
function boxPopOut() {
    infoGroup.transition()
        .duration(500)
        .attr("transform", `translate(${width - boxWidth},50)`);
}

/**
 * 信息提示框隐藏
 */
function boxHide() {
    infoGroup.transition()
        .duration(500)
        .attr("transform", `translate(${width},50)`);
}

/**
 * 找到与一个模块相连的模块，返回名称列表
 * @param module
 */
function findConnected(module) {
    list = [];
    for (let i = 0; i <= module.imports.length - 1; i++) {
        imported = module.imports[i];
        list.push(imported.name);
    }
    for (let i = 0; i <= module.importedBy.length - 1; i++) {
        importing = module.importedBy[i];
        list.push(importing.name);
    }
    return list;
}

/**
 * 将连接的圆形绘制为指定的颜色
 * @param module
 * @param color
 */
function paintConnected(module, color) {
    connected = findConnected(module);
    d3.selectAll("circle")
        .filter(function (d) {
            return connected.indexOf(d.name) !== -1;
        })
        .transition()
        .duration(300)
        .attr("fill", color);
}

/**
 * 主函数
 */
function main() {
    d3.json("static/data/modules.json").then(data => {
        links = data.links;
        nodes = data.nodes;

        renderInit();

        simulation = d3.forceSimulation(nodes)
            .force("manyBody", d3.forceManyBody().strength(-50)) //第一个参数是力的名称
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("link", d3.forceLink(links).strength(0.02).distance(100))
            .on("tick", ticked)
            .alphaDecay(0.03) //使用alpha控制力学模拟终点。alphaDecay设置每次迭代alpha递减的值
            .alphaMin(0.005); //设置alpha最小值
    });
}

main();