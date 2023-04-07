'use strict';

const DEF_TAG = 'div'
const DEF_CLASS = 'pbar'
const DEF_COLOR = 'rgb(72, 149, 239)'
const DEF_BGCOLOR = DEF_COLOR


function round(value, precision)
{
    const power = Math.pow(10, precision || 0)
    return String(Math.round(value * power) / power)
}


// Fancy progress bar implemented as class
// Inpired by: https://alvarotrigo.com/blog/progress-bar-css
class PBar {
    #style
    #_percent   // cached in instance, not to parse css translates

    static #_instances;

    constructor(node_or_id,
                color=DEF_COLOR,
                bgcolor=DEF_BGCOLOR) {
        let node
        if (node_or_id instanceof HTMLElement) {
            node = node_or_id
        } else {
            const name = `${DEF_TAG}${node_or_id}`
            node = document.querySelector(name)
        }

        [this.data, this.#style] = this.constructor.apply_style(node)
        this.node = node
        this.color = color
        this.bgcolor = bgcolor
    }

    static apply_style(node) {
        const fragment = document.createDocumentFragment()
        const bar = document.createElement('div')
        bar.className = 'bar'
        fragment.appendChild(bar)

        const data = document.createElement('div')
        data.className = 'data'
        bar.appendChild(data)

        node.appendChild(fragment)
        return [data, bar.style]
    }

    show() {
        this.node.style.display = 'block'
    }

    hide() {
        this.node.style.display = 'none'
    }

    set percent(val) {
        const perc = round(val, 2)
        const attr = `translate(${perc}%)`
        this.#_percent = val
        this.#style.transform = attr
    }

    get percent() {
        return this.#_percent
    }

    set color(val) {
        this.#style.backgroundColor = val
    }

    set bgcolor(color) {
        const val = `0 0 5px ${color}`
        this.node.style.boxShadow = val
    }

    set colors(color) {
        this.color = color
        this.bgcolor = color
    }

    // method set used to get progress from value in range
    set(val, max=100, min=0) {
        const scale = 100 * (val - min) / (max - min)
        this.percent = scale
    }

    complete() {
        this.percent = 100
    }

    static init_all(color=DEF_COLOR, bgcolor=DEF_BGCOLOR) {
        if (this.#_instances !== undefined) {
            return this.#_instances
        }

        const query = `${DEF_TAG}.${DEF_CLASS}`
        const elems = document.body.querySelectorAll(query)
        const ids = new Map()
        for (const elem of elems) {
            const inst = new this(elem, color, bgcolor)
            ids.set(elem.id, inst)
        }
        this.#_instances = Object.fromEntries(ids.entries())
        return this.#_instances
    }
}
