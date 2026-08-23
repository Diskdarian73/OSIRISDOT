const settings = {
  interval: 3000, // or false
  nodeMap: true,
  nodeStyle: 'rect', // try 'arc' sometime
  stepSpeed: 0.15,

  get glowStyle() {
    return {
      flashMultiplier: this.nodeSize * 20,
      flashUntil: 0.05,
      flashEase: 1/3,
      finalEase: 1/20
    }
  },

  get stormStyle() {
    return {
      minWindAngle: 50,
      maxWindAngle: 70,
      windVariation: 15,
      windSpeedFactor: 1/50,
      windGlowSpeedFactor: 1/max(1, (glowState*3)),
      minParticles: 300,
      maxParticles: 500,
      minParticleLength: G.height/25,
      maxParticleLength: G.height/7,
      maxParticleWidth: G.width/500,
      particleColor: {
        h: 11 + (30 * glowState),
        s: 70,
        l: 24 + (14 * glowState)
      }
    }
  },

  get strokeStyle() {
    return {
      width: this.nodeSize * 4,
      cap: 'round'
    }
  },

  get limits() {
    return {
      strikeSetLimit: 35,
      firstSetMaxStrikes: 2,
      otherSetMaxStrikes: 2,
      dieOff: .9,
      winChance: .15,
      minWinners: ceil(random() * 4),
      stopY: G.height - G.height/100
    }
  },

  get nodeSize() {
    return max(3, G.width / 1000)
  },
  
  get nodeGapConstant() {
    return 8
  },

  get nodeGap() {
    return this.nodeSize * this.nodeGapConstant
  },

  get nodeCount() {
    return floor(
      (G.width * G.height) /
      (this.nodeSize * this.nodeGap) /
      this.nodeGapConstant
    )
  },

  get sizeMultipliers() {
    return {
      y: G.width/25,
      source: G.width/25,
      noise: G.width/70
    }
  },

  get source() {
    return {
      pos: G.pointer,
      treshold: this.nodeSize * 35,
      exponent: 1
    }
  }
}

const G = {
  get frame() {
    return this._frame || 0
  },

  set frame(newFrame) {
    this._frame = newFrame
  },

  get width() {
    return window.innerWidth
  },

  get height() {
    return window.innerHeight
  },

  set pointer(pos) {
    this._pointer = { x: pos.x, y: pos.y }
  },

  get pointer() {
    return this._pointer || {
      x: this.width * 1/3,
      y: this.height * 1/3,
    }
  },

  set click(pos) {
    this._click = { x: pos.x, y: pos.y }
  },

  get click() {
    if (!this._click) {
      this._click = {
        x: this.width / 5 + random() * (this.width * 3/5),
        y: random() * this.height / 3
      }
    }
    return this._click
  }
}

const {
  min, max, abs, sqrt, pow,
  random, round, ceil, floor,
  sin, cos, PI: π
} = Math
const rad = (deg) => deg * π/180
const query = document.querySelector.bind(document)
const clamp = (minV, maxV, value) => min(maxV, max(minV, value))
const calcProgress = (ratio) => clamp(0, 1, ratio)
const calcDistance = (a, b) => sqrt(
  pow(abs(a.x - b.x), 2) +
  pow(abs(a.y - b.y), 2)
)

const fullSize = (el) => {
  el.width = window.innerWidth
  el.height = window.innerHeight
}

const makeLoop = (fn) => {
  return requestAnimationFrame(() => {
    fn()
    makeLoop(fn)
  })
}

const makeArray = (length) => {
  return [
    ...Array(length).keys()
  ].map((_, i) => i)
}

function luckySelect(array, chance, minItems) {
  if (minItems >= array.length) {
    return [...array]
  }
  
  const weighted = array.map(item => ({
    item,
    luck: random(),
    passed: random() < chance
  }))

  const passedItems = weighted
    .filter(w => w.passed)
    .map(w => w.item)

  if (passedItems.length >= minItems) {
    return passedItems
  }

  const failedItems = weighted
    .filter(w => !w.passed)
    .sort((a, b) => a.luck - b.luck)
    .map(w => w.item)

  const needed = minItems - passedItems.length
  return [...passedItems, ...failedItems.slice(0, needed)]
}

const calcNodePos = (nodeIndex) => {
  const size = settings.nodeSize
  const gap = settings.nodeGap
  const x = nodeIndex * (size + gap) % G.width
  const y = floor((nodeIndex * (size + gap)) / G.width) * gap
  return {
    x: x,// + noise.simplex2(x/1, y/1) * (G.width),
    y: y// + noise.simplex2(x/1, y/1) * (G.height)
  }
}

const computeNode = (sourceNode) => (node) => {
  const { nodeSize, sizeMultipliers, source } = settings
  const pos = node.pos || calcNodePos(node)
  const yProgress = node.yProgress || calcProgress(pos.y/G.height)
  const sourceDistance = calcDistance(sourceNode, pos)
  const sourceProgress = calcProgress(source.treshold/sourceDistance)
  const sizeFactorY = sizeMultipliers.y * yProgress
  const sizeFactorSource = pow(sourceProgress, source.exponent) * sizeMultipliers.source
  const sizeFactorNoise = noise.simplex2(pos.x, pos.y) * sizeMultipliers.noise
  return {
    index: node.index || node,
    targeted: node.targeted || false,
    x: pos.x,
    y: pos.y,
    size: sourceProgress * (nodeSize + sizeFactorY + sizeFactorSource + sizeFactorNoise),
    sourceProgress,
    yProgress
  }
}

const computeStrikeState = (rawNodes, computedNodes) => {
  const {
    strikeSetLimit,
    firstSetMaxStrikes,
    otherSetMaxStrikes,
    dieOff,
    stopY
  } = settings.limits
  
  const result = []

  const firstSet =  [...computedNodes]
    .sort((a, b) => b.size - a.size)
    .slice(0, ceil(random() * firstSetMaxStrikes))
    .map(target => ({
      progress: 0,
      from: settings.source.pos,
      to: target
    }))

  firstSet.forEach(strike => {
    computedNodes[strike.to.index].targeted = true
  })

  result.push(firstSet)

  let limit = strikeSetLimit
  while (limit-- > 0) {
    const newSet = []
    const lastSet = result[result.length - 1]
    const sources = lastSet.map(s => s.to)
    if (sources.some(s => s.y >= stopY)) {
      break
    }
    sources.forEach(source => {
      const strikes = rawNodes
        .map((node, i) => {
          return {
            ...computeNode(source)(node),
            targeted: computedNodes[i].targeted
          }
        })
        .filter(node => !node.targeted)
        .filter(node => node.size > source.size * dieOff)
        .sort((a, b) => b.size - a.size)
        .slice(0, ceil(random() * otherSetMaxStrikes))
        .map(newTarget => ({
          progress: 0,
          from: source,
          to: newTarget
        }))
      strikes.forEach(strike => {
        computedNodes[strike.to.index].targeted = true
      })
      newSet.push(...strikes)
    })
    result.push(newSet)
  }

  return result
}

const makeStormParticles = (amount) => {
  const {
    minParticleLength,
    maxParticleLength,
    windSpeedFactor
    } = settings.stormStyle
  return makeArray(round(random() * amount)).map(i => {
    const length = max(minParticleLength, random() * maxParticleLength)
    return {
      x: random() * G.width,
      y: random() * G.height,
      length,
      speed: length * windSpeedFactor
    }
  })
}

const prepareEndStates = () => {
  const {
    flashUntil,
    flashEase,
    finalEase
  } = settings.glowStyle
  strikeState = winnerSets
  if (glowState >= flashUntil) {
    glowState -= glowState * flashEase
  } else {
    glowState -= glowState * finalEase
  }
  endState += (1-endState)/200
}

const prepareWinnerSets = (endSet) => {
  const {
    winChance,
    minWinners,
    stopY,
    strikeSetLimit
  } = settings.limits

  const result = []

  const finishedStrikes = endSet.filter(strike => strike.to.y >= stopY)
  const luckyStrikes = luckySelect(finishedStrikes, winChance, minWinners)
  result.push(luckyStrikes)

  let limit = strikeSetLimit
  while (limit-- > 0) {
    const strikeSet = strikeState.slice(0, -1)[limit]
    if (!strikeSet) continue
    let winningStrikes = []
    for (let i = 0; i < strikeSet.length; i++) {
      const candidateStrike = strikeSet[i]
      for (let j = 0; j < result[0].length; j++) {
        const alreadyWonStrike = result[0][j]
        if (candidateStrike.to.index === alreadyWonStrike.from.index) {
          winningStrikes.push(candidateStrike)
        }
      }
    }
    result.unshift(winningStrikes)
  }

  return result
}

const drawBackground = () => {
  const bgGlowFactor = endState > 0 ? max(1, glowState * 4) : 1
  const bgcolor = `hsl(11, 55%, ${5 * bgGlowFactor}%)`
  ctx.fillStyle = bgcolor
  ctx.fillRect(0, 0, G.width, G.height)
}

const drawNodeMap = (nodes) => {
  // const noiseFactor = noise.simplex2(G.frame/300, 0) * 25
  nodes.forEach(node => {
    const { sourceProgress } = node
    const hue = 43 - drawingState * (G.frame%30)
    const saturation = 20 + 75 * sourceProgress + drawingState * 5
    const lightness = 78 - 14 * sourceProgress - drawingState * 2.5
    ctx.fillStyle = `hsl(${hue}, ${saturation}%, ${lightness}%)`
    const visualWidth = node.size + drawingState * node.size/8
    const visualHeight = node.size * 4 + drawingState * node.size/2
    if (settings.nodeStyle === 'arc') {
      ctx.beginPath()
      ctx.arc(
        node.x - visualWidth/2 + (drawingState * G.frame%12)/3,
        node.y - visualHeight/2 + (drawingState * G.frame%24)/3,
        max(0, visualWidth / 2),
        0,
        2 * π
      )
      ctx.fill()
    } else {
      ctx.fillRect(
        node.x - visualWidth/2 + (drawingState * G.frame%12)/3,
        node.y - visualHeight/2 + (drawingState * G.frame%24)/3,
        visualWidth,
        visualHeight
      )
    }
  })
}

const drawStormParticles = (particles) => {
  const {
    windVariation,
    windGlowSpeedFactor,
    maxParticleWidth,
    particleColor
  } = settings.stormStyle
  particles.forEach(({ x, y, length, speed }, i) => {
    const angle = rad(stormAngle + (x/G.width * windVariation) - (y/G.height * windVariation*2))
    const dirX = sin(angle)
    const dirY = cos(angle)
    ctx.lineCap = 'butt'
    ctx.lineWidth = min(maxParticleWidth, random() * G.width)
    const hue = particleColor.h
    const saturation = particleColor.s
    const lightness = particleColor.l
    ctx.strokeStyle = `hsl(${hue}, ${saturation}%, ${lightness}%)`
    ctx.beginPath()
    ctx.moveTo(x, y)
    ctx.lineTo(x + length * dirX, y + length * dirY)
    ctx.stroke()
    particles[i].x += (length * dirX) * speed * windGlowSpeedFactor
    particles[i].y += (length * dirY) * speed * windGlowSpeedFactor
    if (particles[i].x >= G.width) {
      particles[i].x = -length
      particles[i].y = G.height/-2 + random() * G.height * 2
    }
    if (particles[i].y >= G.height) {
      particles[i].y = random() * -G.height
    }
  })
}

const drawStrikes = () => {
  ctx.strokeStyle = settings.strokeStyle.color
  ctx.lineCap = settings.strokeStyle.cap

  const endGlow = endState > 0 ? (glowState * settings.glowStyle.flashMultiplier) : 1
  const endDisplacement = endState * 25

  strikeState.forEach((strikeSet, i) => {
    const hue = 11 + 32 * (i/30)
    const saturation = 100
    const lightness = 30 + 24 * (i/30)
    ctx.strokeStyle = `hsl(${hue}, ${saturation}%, ${lightness}%)`
    const lineWidth = endGlow * (0.5 + settings.strokeStyle.width * ((i+1)/10))
    ctx.lineWidth = lineWidth
    strikeSet.forEach(strike => {
      if (strike.progress < 1) return
      ctx.beginPath()
      ctx.moveTo(strike.from.x-lineWidth, strike.from.y+endDisplacement)
      ctx.lineTo(strike.to.x-lineWidth, strike.to.y+endDisplacement)
      ctx.stroke()
    })
    const hue2 = 46 - 4 * (i/30)
    const saturation2 = 100
    const lightness2 = 72 + 26 * (i/30)
    ctx.strokeStyle = `hsl(${hue2}, ${saturation2}%, ${lightness2}%)`
    ctx.lineWidth = endGlow * (1 + settings.strokeStyle.width * ((i+1)/12))
    strikeSet.forEach(strike => {
      if (strike.progress < 1) return
      ctx.beginPath()
      ctx.moveTo(strike.from.x, strike.from.y+endDisplacement)
      ctx.lineTo(strike.to.x, strike.to.y+endDisplacement)
      ctx.stroke()
    })
  })
}

const drawActiveStrikes = (activeStrikes) => {
  activeStrikes.forEach(strike => {
    const diffX = strike.to.x - strike.from.x
    const diffY = strike.to.y - strike.from.y
    const x = diffX * strike.progress
    const y = diffY * strike.progress
    ctx.beginPath()
    ctx.moveTo(strike.from.x, strike.from.y)
    ctx.lineTo(
      strike.from.x + x,
      strike.from.y + y
    )
    ctx.stroke()
    strike.progress += settings.stepSpeed
  })
}

const draw = () => {
  G.frame++

  const rawNodes = makeArray(settings.nodeCount)
  const computedNodes = rawNodes.map(computeNode(settings.source.pos))

  if (!stormParticles.length) {
    const { minParticles, maxParticles } = settings.stormStyle
    stormParticles = makeStormParticles(
      minParticles + ceil(random() * (maxParticles - minParticles))
    )
  }

  if (!strikeState.length) {
    strikeState = computeStrikeState(rawNodes, computedNodes)
  }

  const activeStrikes = strikeState.find(strikeSet => {
    return strikeSet.some(strike => strike.progress < 1)
  })

  const endSet = strikeState.find(strikeSet => {
    return strikeSet.some(strike => {
      return strike.to.y >= settings.limits.stopY
    })
  })

  if (!activeStrikes && endSet) {
    prepareEndStates()
  }

  if (endSet && !winnerSets.length) {
    winnerSets = prepareWinnerSets(endSet)
  }

  drawBackground()

  if (settings.nodeMap) {
    drawNodeMap(computedNodes)
  }

  drawStrikes()

  if (activeStrikes) {
    drawingState = min(1, drawingState + max(0.01, drawingState/5))
    drawActiveStrikes(activeStrikes)
  } else {
    drawingState -= drawingState/10
  }

  const { minWindAngle, maxWindAngle } = settings.stormStyle
  stormAngle += noise.simplex2(G.frame/300, 0)
  stormAngle = clamp(minWindAngle, maxWindAngle, stormAngle)
  drawStormParticles(stormParticles)
}

const onResize = () => {
  fullSize(canvas)
}

const onPointerMove = (event) => {
  G.pointer = {
    x: event.x,
    y: event.y - event.y / 3
  }
}

const onClick = (event) => {
  G.click = {
    x: event.x,
    y: event.y
  }
  strikeState = []
  winnerSets = []
  glowState = 1
  endState = 0
  drawingState = 0
  if (settings.interval) {
    clearInterval(strikeInterval)
    strikeInterval = setInterval(() => {
      canvas.click()
    }, settings.interval)
  }
  // noise.seed(random())
}

window.addEventListener('resize', onResize)
window.addEventListener('pointermove', onPointerMove)
window.addEventListener('click', onClick)

const canvas = query('canvas')
const ctx = canvas.getContext('2d')
fullSize(canvas)
makeLoop(draw)
let strikeState = []
let winnerSets = []
let glowState = 1
let endState = 0
let drawingState = 0
let stormParticles = []
let stormAngle = settings.stormStyle.minWindAngle
let strikeInterval

if (settings.interval) {
  strikeInterval = setInterval(() => {
    canvas.click()
  }, settings.interval)
}