// index.js
var Ed = () => {
};
var Ld = () => {
};
function Od(e, t, n) {
  return Array.isArray(e) ? (e.length = Math.max(e.length, t), e.splice(t, 1, n), n) : (e[t] = n, n);
}
function Id(e, t) {
  if (Array.isArray(e)) {
    e.splice(t, 1);
    return;
  }
  delete e[t];
}
var Ad = void 0;
var Nd = Object.freeze(Object.defineProperty({
  __proto__: null,
  Vue2: Ad,
  compile: Ed,
  del: Id,
  install: Ld,
  set: Od
}, Symbol.toStringTag, {
  value: "Module"
}));
var on = (e, t = false) => t ? Symbol.for(e) : Symbol(e);
var Ze = Object.assign;
var hr;
var go = () => hr || (hr = typeof globalThis < "u" ? globalThis : typeof self < "u" ? self : typeof window < "u" ? window : typeof global < "u" ? global : {});
var je = Array.isArray;
var Z = (e) => typeof e == "string";
var Me = (e) => typeof e == "boolean";
var Ce = (e) => e !== null && typeof e == "object";
var De = (e) => {
  if (!Ce(e)) return false;
  const t = Object.getPrototypeOf(e);
  return t === null || t.constructor === Object;
};
function bo(e, t = "") {
  return e.reduce((n, a, s) => s === 0 ? n + a : n + t + a, "");
}
function Vd(e, t, n) {
  return {
    line: e,
    column: t,
    offset: n
  };
}
function Ks(e, t, n) {
  return {
    start: e,
    end: t
  };
}
var ke = {
  EXPECTED_TOKEN: 1,
  INVALID_TOKEN_IN_PLACEHOLDER: 2,
  UNTERMINATED_SINGLE_QUOTE_IN_PLACEHOLDER: 3,
  UNKNOWN_ESCAPE_SEQUENCE: 4,
  INVALID_UNICODE_ESCAPE_SEQUENCE: 5,
  UNBALANCED_CLOSING_BRACE: 6,
  UNTERMINATED_CLOSING_BRACE: 7,
  EMPTY_PLACEHOLDER: 8,
  NOT_ALLOW_NEST_PLACEHOLDER: 9,
  INVALID_LINKED_FORMAT: 10,
  MUST_HAVE_MESSAGES_IN_PLURAL: 11,
  UNEXPECTED_EMPTY_LINKED_MODIFIER: 12,
  UNEXPECTED_EMPTY_LINKED_KEY: 13,
  UNEXPECTED_LEXICAL_ANALYSIS: 14,
  __EXTEND_POINT__: 15
};
function Za(e, t, n = {}) {
  const {
    domain: a,
    messages: s,
    args: r
  } = n, o2 = e, i = new SyntaxError(String(o2));
  return i.code = e, t && (i.location = t), i.domain = a, i;
}
function Ud(e) {
  throw e;
}
var Wt = " ";
var Wd = "\r";
var lt = `
`;
var Hd = "\u2028";
var zd = "\u2029";
function Gd(e) {
  const t = e;
  let n = 0, a = 1, s = 1, r = 0;
  const o2 = (k) => t[k] === Wd && t[k + 1] === lt, i = (k) => t[k] === lt, l = (k) => t[k] === zd, c = (k) => t[k] === Hd, u = (k) => o2(k) || i(k) || l(k) || c(k), h = () => n, p = () => a, v = () => s, w = () => r, $ = (k) => o2(k) || l(k) || c(k) ? lt : t[k], b = () => $(n), m = () => $(n + r);
  function y() {
    return r = 0, u(n) && (a++, s = 0), o2(n) && n++, n++, s++, t[n];
  }
  function S() {
    return o2(n + r) && r++, r++, t[n + r];
  }
  function d() {
    n = 0, a = 1, s = 1, r = 0;
  }
  function f(k = 0) {
    r = k;
  }
  function g() {
    const k = n + r;
    for (; k !== n; ) y();
    r = 0;
  }
  return {
    index: h,
    line: p,
    column: v,
    peekOffset: w,
    charAt: $,
    currentChar: b,
    currentPeek: m,
    next: y,
    peek: S,
    reset: d,
    resetPeek: f,
    skipToPeek: g
  };
}
var Yt = void 0;
var mr = "'";
var Yd = "tokenizer";
function Zd(e, t = {}) {
  const n = t.location !== false, a = Gd(e), s = () => a.index(), r = () => Vd(a.line(), a.column(), a.index()), o2 = r(), i = s(), l = {
    currentType: 14,
    offset: i,
    startLoc: o2,
    endLoc: o2,
    lastType: 14,
    lastOffset: i,
    lastStartLoc: o2,
    lastEndLoc: o2,
    braceNest: 0,
    inLinked: false,
    text: ""
  }, c = () => l, {
    onError: u
  } = t;
  function h(D, T, F, ...W) {
    const re = c();
    if (T.column += F, T.offset += F, u) {
      const be = n ? Ks(re.startLoc, T) : null, ot = Za(D, be, {
        domain: Yd,
        args: W
      });
      u(ot);
    }
  }
  function p(D, T, F) {
    D.endLoc = r(), D.currentType = T;
    const W = {
      type: T
    };
    return n && (W.loc = Ks(D.startLoc, D.endLoc)), F != null && (W.value = F), W;
  }
  const v = (D) => p(D, 14);
  function w(D, T) {
    return D.currentChar() === T ? (D.next(), T) : (h(ke.EXPECTED_TOKEN, r(), 0, T), "");
  }
  function $(D) {
    let T = "";
    for (; D.currentPeek() === Wt || D.currentPeek() === lt; ) T += D.currentPeek(), D.peek();
    return T;
  }
  function b(D) {
    const T = $(D);
    return D.skipToPeek(), T;
  }
  function m(D) {
    if (D === Yt) return false;
    const T = D.charCodeAt(0);
    return T >= 97 && T <= 122 || T >= 65 && T <= 90 || T === 95;
  }
  function y(D) {
    if (D === Yt) return false;
    const T = D.charCodeAt(0);
    return T >= 48 && T <= 57;
  }
  function S(D, T) {
    const {
      currentType: F
    } = T;
    if (F !== 2) return false;
    $(D);
    const W = m(D.currentPeek());
    return D.resetPeek(), W;
  }
  function d(D, T) {
    const {
      currentType: F
    } = T;
    if (F !== 2) return false;
    $(D);
    const W = D.currentPeek() === "-" ? D.peek() : D.currentPeek(), re = y(W);
    return D.resetPeek(), re;
  }
  function f(D, T) {
    const {
      currentType: F
    } = T;
    if (F !== 2) return false;
    $(D);
    const W = D.currentPeek() === mr;
    return D.resetPeek(), W;
  }
  function g(D, T) {
    const {
      currentType: F
    } = T;
    if (F !== 8) return false;
    $(D);
    const W = D.currentPeek() === ".";
    return D.resetPeek(), W;
  }
  function k(D, T) {
    const {
      currentType: F
    } = T;
    if (F !== 9) return false;
    $(D);
    const W = m(D.currentPeek());
    return D.resetPeek(), W;
  }
  function M(D, T) {
    const {
      currentType: F
    } = T;
    if (!(F === 8 || F === 12)) return false;
    $(D);
    const W = D.currentPeek() === ":";
    return D.resetPeek(), W;
  }
  function A(D, T) {
    const {
      currentType: F
    } = T;
    if (F !== 10) return false;
    const W = () => {
      const be = D.currentPeek();
      return be === "{" ? m(D.peek()) : be === "@" || be === "%" || be === "|" || be === ":" || be === "." || be === Wt || !be ? false : be === lt ? (D.peek(), W()) : m(be);
    }, re = W();
    return D.resetPeek(), re;
  }
  function I(D) {
    $(D);
    const T = D.currentPeek() === "|";
    return D.resetPeek(), T;
  }
  function oe(D) {
    const T = $(D), F = D.currentPeek() === "%" && D.peek() === "{";
    return D.resetPeek(), {
      isModulo: F,
      hasSpace: T.length > 0
    };
  }
  function ce(D, T = true) {
    const F = (re = false, be = "", ot = false) => {
      const Fe = D.currentPeek();
      return Fe === "{" ? be === "%" ? false : re : Fe === "@" || !Fe ? be === "%" ? true : re : Fe === "%" ? (D.peek(), F(re, "%", true)) : Fe === "|" ? be === "%" || ot ? true : !(be === Wt || be === lt) : Fe === Wt ? (D.peek(), F(true, Wt, ot)) : Fe === lt ? (D.peek(), F(true, lt, ot)) : true;
    }, W = F();
    return T && D.resetPeek(), W;
  }
  function R(D, T) {
    const F = D.currentChar();
    return F === Yt ? Yt : T(F) ? (D.next(), F) : null;
  }
  function N(D) {
    return R(D, (F) => {
      const W = F.charCodeAt(0);
      return W >= 97 && W <= 122 || W >= 65 && W <= 90 || W >= 48 && W <= 57 || W === 95 || W === 36;
    });
  }
  function B(D) {
    return R(D, (F) => {
      const W = F.charCodeAt(0);
      return W >= 48 && W <= 57;
    });
  }
  function G(D) {
    return R(D, (F) => {
      const W = F.charCodeAt(0);
      return W >= 48 && W <= 57 || W >= 65 && W <= 70 || W >= 97 && W <= 102;
    });
  }
  function j(D) {
    let T = "", F = "";
    for (; T = B(D); ) F += T;
    return F;
  }
  function J(D) {
    b(D);
    const T = D.currentChar();
    return T !== "%" && h(ke.EXPECTED_TOKEN, r(), 0, T), D.next(), "%";
  }
  function q(D) {
    let T = "";
    for (; ; ) {
      const F = D.currentChar();
      if (F === "{" || F === "}" || F === "@" || F === "|" || !F) break;
      if (F === "%") if (ce(D)) T += F, D.next();
      else break;
      else if (F === Wt || F === lt) if (ce(D)) T += F, D.next();
      else {
        if (I(D)) break;
        T += F, D.next();
      }
      else T += F, D.next();
    }
    return T;
  }
  function fe(D) {
    b(D);
    let T = "", F = "";
    for (; T = N(D); ) F += T;
    return D.currentChar() === Yt && h(ke.UNTERMINATED_CLOSING_BRACE, r(), 0), F;
  }
  function we(D) {
    b(D);
    let T = "";
    return D.currentChar() === "-" ? (D.next(), T += `-${j(D)}`) : T += j(D), D.currentChar() === Yt && h(ke.UNTERMINATED_CLOSING_BRACE, r(), 0), T;
  }
  function ge(D) {
    b(D), w(D, "'");
    let T = "", F = "";
    const W = (be) => be !== mr && be !== lt;
    for (; T = R(D, W); ) T === "\\" ? F += Te(D) : F += T;
    const re = D.currentChar();
    return re === lt || re === Yt ? (h(ke.UNTERMINATED_SINGLE_QUOTE_IN_PLACEHOLDER, r(), 0), re === lt && (D.next(), w(D, "'")), F) : (w(D, "'"), F);
  }
  function Te(D) {
    const T = D.currentChar();
    switch (T) {
      case "\\":
      case "'":
        return D.next(), `\\${T}`;
      case "u":
        return x(D, T, 4);
      case "U":
        return x(D, T, 6);
      default:
        return h(ke.UNKNOWN_ESCAPE_SEQUENCE, r(), 0, T), "";
    }
  }
  function x(D, T, F) {
    w(D, T);
    let W = "";
    for (let re = 0; re < F; re++) {
      const be = G(D);
      if (!be) {
        h(ke.INVALID_UNICODE_ESCAPE_SEQUENCE, r(), 0, `\\${T}${W}${D.currentChar()}`);
        break;
      }
      W += be;
    }
    return `\\${T}${W}`;
  }
  function U(D) {
    b(D);
    let T = "", F = "";
    const W = (re) => re !== "{" && re !== "}" && re !== Wt && re !== lt;
    for (; T = R(D, W); ) F += T;
    return F;
  }
  function le(D) {
    let T = "", F = "";
    for (; T = N(D); ) F += T;
    return F;
  }
  function _e(D) {
    const T = (F = false, W) => {
      const re = D.currentChar();
      return re === "{" || re === "%" || re === "@" || re === "|" || !re || re === Wt ? W : re === lt ? (W += re, D.next(), T(F, W)) : (W += re, D.next(), T(true, W));
    };
    return T(false, "");
  }
  function ve(D) {
    b(D);
    const T = w(D, "|");
    return b(D), T;
  }
  function he(D, T) {
    let F = null;
    switch (D.currentChar()) {
      case "{":
        return T.braceNest >= 1 && h(ke.NOT_ALLOW_NEST_PLACEHOLDER, r(), 0), D.next(), F = p(T, 2, "{"), b(D), T.braceNest++, F;
      case "}":
        return T.braceNest > 0 && T.currentType === 2 && h(ke.EMPTY_PLACEHOLDER, r(), 0), D.next(), F = p(T, 3, "}"), T.braceNest--, T.braceNest > 0 && b(D), T.inLinked && T.braceNest === 0 && (T.inLinked = false), F;
      case "@":
        return T.braceNest > 0 && h(ke.UNTERMINATED_CLOSING_BRACE, r(), 0), F = Pe(D, T) || v(T), T.braceNest = 0, F;
      default:
        let re = true, be = true, ot = true;
        if (I(D)) return T.braceNest > 0 && h(ke.UNTERMINATED_CLOSING_BRACE, r(), 0), F = p(T, 1, ve(D)), T.braceNest = 0, T.inLinked = false, F;
        if (T.braceNest > 0 && (T.currentType === 5 || T.currentType === 6 || T.currentType === 7)) return h(ke.UNTERMINATED_CLOSING_BRACE, r(), 0), T.braceNest = 0, Ve(D, T);
        if (re = S(D, T)) return F = p(T, 5, fe(D)), b(D), F;
        if (be = d(D, T)) return F = p(T, 6, we(D)), b(D), F;
        if (ot = f(D, T)) return F = p(T, 7, ge(D)), b(D), F;
        if (!re && !be && !ot) return F = p(T, 13, U(D)), h(ke.INVALID_TOKEN_IN_PLACEHOLDER, r(), 0, F.value), b(D), F;
        break;
    }
    return F;
  }
  function Pe(D, T) {
    const {
      currentType: F
    } = T;
    let W = null;
    const re = D.currentChar();
    switch ((F === 8 || F === 9 || F === 12 || F === 10) && (re === lt || re === Wt) && h(ke.INVALID_LINKED_FORMAT, r(), 0), re) {
      case "@":
        return D.next(), W = p(T, 8, "@"), T.inLinked = true, W;
      case ".":
        return b(D), D.next(), p(T, 9, ".");
      case ":":
        return b(D), D.next(), p(T, 10, ":");
      default:
        return I(D) ? (W = p(T, 1, ve(D)), T.braceNest = 0, T.inLinked = false, W) : g(D, T) || M(D, T) ? (b(D), Pe(D, T)) : k(D, T) ? (b(D), p(T, 12, le(D))) : A(D, T) ? (b(D), re === "{" ? he(D, T) || W : p(T, 11, _e(D))) : (F === 8 && h(ke.INVALID_LINKED_FORMAT, r(), 0), T.braceNest = 0, T.inLinked = false, Ve(D, T));
    }
  }
  function Ve(D, T) {
    let F = {
      type: 14
    };
    if (T.braceNest > 0) return he(D, T) || v(T);
    if (T.inLinked) return Pe(D, T) || v(T);
    switch (D.currentChar()) {
      case "{":
        return he(D, T) || v(T);
      case "}":
        return h(ke.UNBALANCED_CLOSING_BRACE, r(), 0), D.next(), p(T, 3, "}");
      case "@":
        return Pe(D, T) || v(T);
      default:
        if (I(D)) return F = p(T, 1, ve(D)), T.braceNest = 0, T.inLinked = false, F;
        const {
          isModulo: re,
          hasSpace: be
        } = oe(D);
        if (re) return be ? p(T, 0, q(D)) : p(T, 4, J(D));
        if (ce(D)) return p(T, 0, q(D));
        break;
    }
    return F;
  }
  function gt() {
    const {
      currentType: D,
      offset: T,
      startLoc: F,
      endLoc: W
    } = l;
    return l.lastType = D, l.lastOffset = T, l.lastStartLoc = F, l.lastEndLoc = W, l.offset = s(), l.startLoc = r(), a.currentChar() === Yt ? p(l, 14) : Ve(a, l);
  }
  return {
    nextToken: gt,
    currentOffset: s,
    currentPosition: r,
    context: c
  };
}
var Kd = "parser";
var qd = /(?:\\\\|\\'|\\u([0-9a-fA-F]{4})|\\U([0-9a-fA-F]{6}))/g;
function Xd(e, t, n) {
  switch (e) {
    case "\\\\":
      return "\\";
    case "\\'":
      return "'";
    default: {
      const a = parseInt(t || n, 16);
      return a <= 55295 || a >= 57344 ? String.fromCodePoint(a) : "\uFFFD";
    }
  }
}
function Jd(e = {}) {
  const t = e.location !== false, {
    onError: n
  } = e;
  function a(m, y, S, d, ...f) {
    const g = m.currentPosition();
    if (g.offset += d, g.column += d, n) {
      const k = t ? Ks(S, g) : null, M = Za(y, k, {
        domain: Kd,
        args: f
      });
      n(M);
    }
  }
  function s(m, y, S) {
    const d = {
      type: m
    };
    return t && (d.start = y, d.end = y, d.loc = {
      start: S,
      end: S
    }), d;
  }
  function r(m, y, S, d) {
    t && (m.end = y, m.loc && (m.loc.end = S));
  }
  function o2(m, y) {
    const S = m.context(), d = s(3, S.offset, S.startLoc);
    return d.value = y, r(d, m.currentOffset(), m.currentPosition()), d;
  }
  function i(m, y) {
    const S = m.context(), {
      lastOffset: d,
      lastStartLoc: f
    } = S, g = s(5, d, f);
    return g.index = parseInt(y, 10), m.nextToken(), r(g, m.currentOffset(), m.currentPosition()), g;
  }
  function l(m, y) {
    const S = m.context(), {
      lastOffset: d,
      lastStartLoc: f
    } = S, g = s(4, d, f);
    return g.key = y, m.nextToken(), r(g, m.currentOffset(), m.currentPosition()), g;
  }
  function c(m, y) {
    const S = m.context(), {
      lastOffset: d,
      lastStartLoc: f
    } = S, g = s(9, d, f);
    return g.value = y.replace(qd, Xd), m.nextToken(), r(g, m.currentOffset(), m.currentPosition()), g;
  }
  function u(m) {
    const y = m.nextToken(), S = m.context(), {
      lastOffset: d,
      lastStartLoc: f
    } = S, g = s(8, d, f);
    return y.type !== 12 ? (a(m, ke.UNEXPECTED_EMPTY_LINKED_MODIFIER, S.lastStartLoc, 0), g.value = "", r(g, d, f), {
      nextConsumeToken: y,
      node: g
    }) : (y.value == null && a(m, ke.UNEXPECTED_LEXICAL_ANALYSIS, S.lastStartLoc, 0, Nt(y)), g.value = y.value || "", r(g, m.currentOffset(), m.currentPosition()), {
      node: g
    });
  }
  function h(m, y) {
    const S = m.context(), d = s(7, S.offset, S.startLoc);
    return d.value = y, r(d, m.currentOffset(), m.currentPosition()), d;
  }
  function p(m) {
    const y = m.context(), S = s(6, y.offset, y.startLoc);
    let d = m.nextToken();
    if (d.type === 9) {
      const f = u(m);
      S.modifier = f.node, d = f.nextConsumeToken || m.nextToken();
    }
    switch (d.type !== 10 && a(m, ke.UNEXPECTED_LEXICAL_ANALYSIS, y.lastStartLoc, 0, Nt(d)), d = m.nextToken(), d.type === 2 && (d = m.nextToken()), d.type) {
      case 11:
        d.value == null && a(m, ke.UNEXPECTED_LEXICAL_ANALYSIS, y.lastStartLoc, 0, Nt(d)), S.key = h(m, d.value || "");
        break;
      case 5:
        d.value == null && a(m, ke.UNEXPECTED_LEXICAL_ANALYSIS, y.lastStartLoc, 0, Nt(d)), S.key = l(m, d.value || "");
        break;
      case 6:
        d.value == null && a(m, ke.UNEXPECTED_LEXICAL_ANALYSIS, y.lastStartLoc, 0, Nt(d)), S.key = i(m, d.value || "");
        break;
      case 7:
        d.value == null && a(m, ke.UNEXPECTED_LEXICAL_ANALYSIS, y.lastStartLoc, 0, Nt(d)), S.key = c(m, d.value || "");
        break;
      default:
        a(m, ke.UNEXPECTED_EMPTY_LINKED_KEY, y.lastStartLoc, 0);
        const f = m.context(), g = s(7, f.offset, f.startLoc);
        return g.value = "", r(g, f.offset, f.startLoc), S.key = g, r(S, f.offset, f.startLoc), {
          nextConsumeToken: d,
          node: S
        };
    }
    return r(S, m.currentOffset(), m.currentPosition()), {
      node: S
    };
  }
  function v(m) {
    const y = m.context(), S = y.currentType === 1 ? m.currentOffset() : y.offset, d = y.currentType === 1 ? y.endLoc : y.startLoc, f = s(2, S, d);
    f.items = [];
    let g = null;
    do {
      const A = g || m.nextToken();
      switch (g = null, A.type) {
        case 0:
          A.value == null && a(m, ke.UNEXPECTED_LEXICAL_ANALYSIS, y.lastStartLoc, 0, Nt(A)), f.items.push(o2(m, A.value || ""));
          break;
        case 6:
          A.value == null && a(m, ke.UNEXPECTED_LEXICAL_ANALYSIS, y.lastStartLoc, 0, Nt(A)), f.items.push(i(m, A.value || ""));
          break;
        case 5:
          A.value == null && a(m, ke.UNEXPECTED_LEXICAL_ANALYSIS, y.lastStartLoc, 0, Nt(A)), f.items.push(l(m, A.value || ""));
          break;
        case 7:
          A.value == null && a(m, ke.UNEXPECTED_LEXICAL_ANALYSIS, y.lastStartLoc, 0, Nt(A)), f.items.push(c(m, A.value || ""));
          break;
        case 8:
          const I = p(m);
          f.items.push(I.node), g = I.nextConsumeToken || null;
          break;
      }
    } while (y.currentType !== 14 && y.currentType !== 1);
    const k = y.currentType === 1 ? y.lastOffset : m.currentOffset(), M = y.currentType === 1 ? y.lastEndLoc : m.currentPosition();
    return r(f, k, M), f;
  }
  function w(m, y, S, d) {
    const f = m.context();
    let g = d.items.length === 0;
    const k = s(1, y, S);
    k.cases = [], k.cases.push(d);
    do {
      const M = v(m);
      g || (g = M.items.length === 0), k.cases.push(M);
    } while (f.currentType !== 14);
    return g && a(m, ke.MUST_HAVE_MESSAGES_IN_PLURAL, S, 0), r(k, m.currentOffset(), m.currentPosition()), k;
  }
  function $(m) {
    const y = m.context(), {
      offset: S,
      startLoc: d
    } = y, f = v(m);
    return y.currentType === 14 ? f : w(m, S, d, f);
  }
  function b(m) {
    const y = Zd(m, Ze({}, e)), S = y.context(), d = s(0, S.offset, S.startLoc);
    return t && d.loc && (d.loc.source = m), d.body = $(y), e.onCacheKey && (d.cacheKey = e.onCacheKey(m)), S.currentType !== 14 && a(y, ke.UNEXPECTED_LEXICAL_ANALYSIS, S.lastStartLoc, 0, m[S.offset] || ""), r(d, y.currentOffset(), y.currentPosition()), d;
  }
  return {
    parse: b
  };
}
function Nt(e) {
  if (e.type === 14) return "EOF";
  const t = (e.value || "").replace(/\r?\n/gu, "\\n");
  return t.length > 10 ? t.slice(0, 9) + "\u2026" : t;
}
function Qd(e, t = {}) {
  const n = {
    ast: e,
    helpers: /* @__PURE__ */ new Set()
  };
  return {
    context: () => n,
    helper: (r) => (n.helpers.add(r), r)
  };
}
function gr(e, t) {
  for (let n = 0; n < e.length; n++) yo(e[n], t);
}
function yo(e, t) {
  switch (e.type) {
    case 1:
      gr(e.cases, t), t.helper("plural");
      break;
    case 2:
      gr(e.items, t);
      break;
    case 6:
      yo(e.key, t), t.helper("linked"), t.helper("type");
      break;
    case 5:
      t.helper("interpolate"), t.helper("list");
      break;
    case 4:
      t.helper("interpolate"), t.helper("named");
      break;
  }
}
function ef(e, t = {}) {
  const n = Qd(e);
  n.helper("normalize"), e.body && yo(e.body, n);
  const a = n.context();
  e.helpers = Array.from(a.helpers);
}
function tf(e) {
  const t = e.body;
  return t.type === 2 ? vr(t) : t.cases.forEach((n) => vr(n)), e;
}
function vr(e) {
  if (e.items.length === 1) {
    const t = e.items[0];
    (t.type === 3 || t.type === 9) && (e.static = t.value, delete t.value);
  } else {
    const t = [];
    for (let n = 0; n < e.items.length; n++) {
      const a = e.items[n];
      if (!(a.type === 3 || a.type === 9) || a.value == null) break;
      t.push(a.value);
    }
    if (t.length === e.items.length) {
      e.static = bo(t);
      for (let n = 0; n < e.items.length; n++) {
        const a = e.items[n];
        (a.type === 3 || a.type === 9) && delete a.value;
      }
    }
  }
}
function nf(e, t) {
  const {
    sourceMap: n,
    filename: a,
    breakLineCode: s,
    needIndent: r
  } = t, o2 = t.location !== false, i = {
    filename: a,
    code: "",
    column: 1,
    line: 1,
    offset: 0,
    map: void 0,
    breakLineCode: s,
    needIndent: r,
    indentLevel: 0
  };
  o2 && e.loc && (i.source = e.loc.source);
  const l = () => i;
  function c(b, m) {
    i.code += b;
  }
  function u(b, m = true) {
    const y = m ? s : "";
    c(r ? y + "  ".repeat(b) : y);
  }
  function h(b = true) {
    const m = ++i.indentLevel;
    b && u(m);
  }
  function p(b = true) {
    const m = --i.indentLevel;
    b && u(m);
  }
  function v() {
    u(i.indentLevel);
  }
  return {
    context: l,
    push: c,
    indent: h,
    deindent: p,
    newline: v,
    helper: (b) => `_${b}`,
    needIndent: () => i.needIndent
  };
}
function af(e, t) {
  const {
    helper: n
  } = e;
  e.push(`${n("linked")}(`), kn(e, t.key), t.modifier ? (e.push(", "), kn(e, t.modifier), e.push(", _type")) : e.push(", undefined, _type"), e.push(")");
}
function sf(e, t) {
  const {
    helper: n,
    needIndent: a
  } = e;
  e.push(`${n("normalize")}([`), e.indent(a());
  const s = t.items.length;
  for (let r = 0; r < s && (kn(e, t.items[r]), r !== s - 1); r++) e.push(", ");
  e.deindent(a()), e.push("])");
}
function of(e, t) {
  const {
    helper: n,
    needIndent: a
  } = e;
  if (t.cases.length > 1) {
    e.push(`${n("plural")}([`), e.indent(a());
    const s = t.cases.length;
    for (let r = 0; r < s && (kn(e, t.cases[r]), r !== s - 1); r++) e.push(", ");
    e.deindent(a()), e.push("])");
  }
}
function rf(e, t) {
  t.body ? kn(e, t.body) : e.push("null");
}
function kn(e, t) {
  const {
    helper: n
  } = e;
  switch (t.type) {
    case 0:
      rf(e, t);
      break;
    case 1:
      of(e, t);
      break;
    case 2:
      sf(e, t);
      break;
    case 6:
      af(e, t);
      break;
    case 8:
      e.push(JSON.stringify(t.value), t);
      break;
    case 7:
      e.push(JSON.stringify(t.value), t);
      break;
    case 5:
      e.push(`${n("interpolate")}(${n("list")}(${t.index}))`, t);
      break;
    case 4:
      e.push(`${n("interpolate")}(${n("named")}(${JSON.stringify(t.key)}))`, t);
      break;
    case 9:
      e.push(JSON.stringify(t.value), t);
      break;
    case 3:
      e.push(JSON.stringify(t.value), t);
      break;
  }
}
var lf = (e, t = {}) => {
  const n = Z(t.mode) ? t.mode : "normal", a = Z(t.filename) ? t.filename : "message.intl", s = !!t.sourceMap, r = t.breakLineCode != null ? t.breakLineCode : n === "arrow" ? ";" : `
`, o2 = t.needIndent ? t.needIndent : n !== "arrow", i = e.helpers || [], l = nf(e, {
    mode: n,
    filename: a,
    sourceMap: s,
    breakLineCode: r,
    needIndent: o2
  });
  l.push(n === "normal" ? "function __msg__ (ctx) {" : "(ctx) => {"), l.indent(o2), i.length > 0 && (l.push(`const { ${bo(i.map((h) => `${h}: _${h}`), ", ")} } = ctx`), l.newline()), l.push("return "), kn(l, e), l.deindent(o2), l.push("}"), delete e.helpers;
  const {
    code: c,
    map: u
  } = l.context();
  return {
    ast: e,
    code: c,
    map: u ? u.toJSON() : void 0
  };
};
function cf(e, t = {}) {
  const n = Ze({}, t), a = !!n.jit, s = n.optimize == null ? true : n.optimize, o2 = Jd(n).parse(e);
  return a ? (s && tf(o2), {
    ast: o2,
    code: ""
  }) : (ef(o2, n), lf(o2, n));
}
var Yi = {
  I18nInit: "i18n:init",
  FunctionTranslate: "function:translate"
};
function uf() {
  typeof __INTLIFY_PROD_DEVTOOLS__ != "boolean" && (go().__INTLIFY_PROD_DEVTOOLS__ = false);
}
var Xt = [];
Xt[0] = {
  w: [0],
  i: [3, 0],
  "[": [4],
  o: [7]
};
Xt[1] = {
  w: [1],
  ".": [2],
  "[": [4],
  o: [7]
};
Xt[2] = {
  w: [2],
  i: [3, 0],
  0: [3, 0]
};
Xt[3] = {
  i: [3, 0],
  0: [3, 0],
  w: [1, 1],
  ".": [2, 1],
  "[": [4, 1],
  o: [7, 1]
};
Xt[4] = {
  "'": [5, 0],
  '"': [6, 0],
  "[": [4, 2],
  "]": [1, 3],
  o: 8,
  l: [4, 0]
};
Xt[5] = {
  "'": [4, 0],
  o: 8,
  l: [5, 0]
};
Xt[6] = {
  '"': [4, 0],
  o: 8,
  l: [6, 0]
};
var df = /^\s?(?:true|false|-?[\d.]+|'[^']*'|"[^"]*")\s?$/;
function ff(e) {
  return df.test(e);
}
function hf(e) {
  const t = e.charCodeAt(0), n = e.charCodeAt(e.length - 1);
  return t === n && (t === 34 || t === 39) ? e.slice(1, -1) : e;
}
function pf(e) {
  if (e == null) return "o";
  switch (e.charCodeAt(0)) {
    case 91:
    case 93:
    case 46:
    case 34:
    case 39:
      return e;
    case 95:
    case 36:
    case 45:
      return "i";
    case 9:
    case 10:
    case 13:
    case 160:
    case 65279:
    case 8232:
    case 8233:
      return "w";
  }
  return "i";
}
function mf(e) {
  const t = e.trim();
  return e.charAt(0) === "0" && isNaN(parseInt(e)) ? false : ff(t) ? hf(t) : "*" + t;
}
function gf(e) {
  const t = [];
  let n = -1, a = 0, s = 0, r, o2, i, l, c, u, h;
  const p = [];
  p[0] = () => {
    o2 === void 0 ? o2 = i : o2 += i;
  }, p[1] = () => {
    o2 !== void 0 && (t.push(o2), o2 = void 0);
  }, p[2] = () => {
    p[0](), s++;
  }, p[3] = () => {
    if (s > 0) s--, a = 4, p[0]();
    else {
      if (s = 0, o2 === void 0 || (o2 = mf(o2), o2 === false)) return false;
      p[1]();
    }
  };
  function v() {
    const w = e[n + 1];
    if (a === 5 && w === "'" || a === 6 && w === '"') return n++, i = "\\" + w, p[0](), true;
  }
  for (; a !== null; ) if (n++, r = e[n], !(r === "\\" && v())) {
    if (l = pf(r), h = Xt[a], c = h[l] || h.l || 8, c === 8 || (a = c[0], c[1] !== void 0 && (u = p[c[1]], u && (i = r, u() === false)))) return;
    if (a === 7) return t;
  }
}
var br = /* @__PURE__ */ new Map();
function bf(e, t) {
  if (!Ce(e)) return null;
  let n = br.get(t);
  if (n || (n = gf(t), n && br.set(t, n)), !n) return null;
  const a = n.length;
  let s = e, r = 0;
  for (; r < a; ) {
    const o2 = s[n[r]];
    if (o2 === void 0) return null;
    s = o2, r++;
  }
  return s;
}
var ea = null;
function _f(e) {
  ea = e;
}
var Lf = Of(Yi.FunctionTranslate);
function Of(e) {
  return (t) => ea && ea.emit(e, t);
}
function Zi(e, t, n) {
  const a = Z(n) ? n : $o, s = e;
  s.__localeChainCache || (s.__localeChainCache = /* @__PURE__ */ new Map());
  let r = s.__localeChainCache.get(a);
  if (!r) {
    r = [];
    let o2 = [n];
    for (; je(o2); ) o2 = $r(r, o2, t);
    const i = je(t) || !De(t) ? t : t.default ? t.default : null;
    o2 = Z(i) ? [i] : i, je(o2) && $r(r, o2, false), s.__localeChainCache.set(a, r);
  }
  return r;
}
function $r(e, t, n) {
  let a = true;
  for (let s = 0; s < t.length && Me(a); s++) {
    const r = t[s];
    Z(r) && (a = Af(e, t[s], n));
  }
  return a;
}
function Af(e, t, n) {
  let a;
  const s = t.split("-");
  do {
    const r = s.join("-");
    a = Pf(e, r, n), s.splice(-1, 1);
  } while (s.length && a === true);
  return a;
}
function Pf(e, t, n) {
  let a = false;
  if (!e.includes(t) && (a = true, t)) {
    a = t[t.length - 1] !== "!";
    const s = t.replace(/!/g, "");
    e.push(s), (je(n) || De(n)) && n[s] && (a = n[s]);
  }
  return a;
}
var $o = "en-US";
var Ki;
function Rf(e) {
  Ki = e;
}
var qi;
function Ff(e) {
  qi = e;
}
var Xi;
function Bf(e) {
  Xi = e;
}
function Ds(e) {
  return (n) => Uf(n, e);
}
function Uf(e, t) {
  return t.body.type === 1 ? e.plural(t.body.cases.reduce((n, a) => [...n, Tr(e, a)], [])) : Tr(e, t.body);
}
function Tr(e, t) {
  if (t.static) return e.type === "text" ? t.static : e.normalize([t.static]);
  {
    const n = t.items.reduce((a, s) => [...a, qs(e, s)], []);
    return e.normalize(n);
  }
}
function qs(e, t) {
  switch (t.type) {
    case 3:
      return t.value;
    case 9:
      return t.value;
    case 4:
      return e.interpolate(e.named(t.key));
    case 5:
      return e.interpolate(e.list(t.index));
    case 6:
      return e.linked(qs(e, t.key), t.modifier ? qs(e, t.modifier) : void 0, e.type);
    case 7:
      return t.value;
    case 8:
      return t.value;
    default:
      throw new Error(`unhandled node type on format message part: ${t.type}`);
  }
}
var el = ke.__EXTEND_POINT__;
var wa = () => ++el;
var yn = {
  INVALID_ARGUMENT: el,
  INVALID_DATE_ARGUMENT: wa(),
  INVALID_ISO_DATE_ARGUMENT: wa(),
  NOT_SUPPORT_AST: wa(),
  __EXTEND_POINT__: wa()
};
var Wf = (e) => e;
var ka = /* @__PURE__ */ Object.create(null);
function Hf(e, t = {}) {
  let n = false;
  const a = t.onError || Ud;
  return t.onError = (s) => {
    n = true, a(s);
  }, {
    ...cf(e, t),
    detectError: n
  };
}
function zf(e, t = {}) {
  if (Z(e)) {
    Me(t.warnHtmlMessage) && t.warnHtmlMessage;
    const a = (t.onCacheKey || Wf)(e), s = ka[a];
    if (s) return s;
    const {
      ast: r,
      detectError: o2
    } = Hf(e, {
      ...t,
      location: false,
      jit: true
    }), i = Ds(r);
    return o2 ? i : ka[a] = i;
  } else {
    const n = e.cacheKey;
    if (n) {
      const a = ka[n];
      return a || (ka[n] = Ds(e));
    } else return Ds(e);
  }
}
uf();
function Xf() {
  typeof __INTLIFY_PROD_DEVTOOLS__ != "boolean" && (go().__INTLIFY_PROD_DEVTOOLS__ = false);
}
var ol = ke.__EXTEND_POINT__;
var dt = () => ++ol;
var yt = {
  UNEXPECTED_RETURN_TYPE: ol,
  INVALID_ARGUMENT: dt(),
  MUST_BE_CALL_SETUP_TOP: dt(),
  NOT_INSTALLED: dt(),
  NOT_AVAILABLE_IN_LEGACY_MODE: dt(),
  REQUIRED_VALUE: dt(),
  INVALID_VALUE: dt(),
  CANNOT_SETUP_VUE_DEVTOOLS_PLUGIN: dt(),
  NOT_INSTALLED_WITH_PROVIDE: dt(),
  UNEXPECTED_ERROR: dt(),
  NOT_COMPATIBLE_LEGACY_VUE_I18N: dt(),
  BRIDGE_SUPPORT_VUE_2_ONLY: dt(),
  MUST_DEFINE_I18N_OPTION_IN_ALLOW_COMPOSITION: dt(),
  NOT_AVAILABLE_COMPOSITION_IN_LEGACY: dt(),
  __EXTEND_POINT__: dt()
};
var eo = on("__translateVNode");
var to = on("__datetimeParts");
var no = on("__numberParts");
var Jf = on("__setPluralRules");
var Qf = on("__injectWithOption");
var uh = on("global-vue-i18n");
Xf();
Rf(zf);
Ff(bf);
Bf(Zi);
if (__INTLIFY_PROD_DEVTOOLS__) {
  const e = go();
  e.__INTLIFY__ = true, _f(e.__INTLIFY_DEVTOOLS_GLOBAL_HOOK__);
}
var Eh = function(e) {
  function t(a) {
    if (n[a]) return n[a].exports;
    var s = n[a] = {
      i: a,
      l: false,
      exports: {}
    };
    return e[a].call(s.exports, s, s.exports, t), s.l = true, s.exports;
  }
  var n = {};
  return t.m = e, t.c = n, t.d = function(a, s, r) {
    t.o(a, s) || Object.defineProperty(a, s, {
      configurable: false,
      enumerable: true,
      get: r
    });
  }, t.n = function(a) {
    var s = a && a.__esModule ? function() {
      return a.default;
    } : function() {
      return a;
    };
    return t.d(s, "a", s), s;
  }, t.o = function(a, s) {
    return Object.prototype.hasOwnProperty.call(a, s);
  }, t.p = "", t(t.s = 0);
}([function(e, t, n) {
  var a = typeof Symbol == "function" && typeof Symbol.iterator == "symbol" ? function(r) {
    return typeof r;
  } : function(r) {
    return r && typeof Symbol == "function" && r.constructor === Symbol && r !== Symbol.prototype ? "symbol" : typeof r;
  }, s = n(1);
  e.exports = function(r, o2) {
    var i = !(arguments.length > 2 && arguments[2] !== void 0) || arguments[2], l = (typeof document > "u" ? "undefined" : a(document)) === "object" && typeof document.cookie == "string", c = (r === void 0 ? "undefined" : a(r)) === "object" && (o2 === void 0 ? "undefined" : a(o2)) === "object" && e !== void 0, u = !l && !c || l && c, h = function(b) {
      if (c) {
        var m = r.headers.cookie || "";
        return b && (m = o2.getHeaders(), m = m["set-cookie"] ? m["set-cookie"].map(function(y) {
          return y.split(";")[0];
        }).join(";") : ""), m;
      }
      if (l) return document.cookie || "";
    }, p = function() {
      var b = o2.getHeader("Set-Cookie");
      return (b = typeof b == "string" ? [b] : b) || [];
    }, v = function(b) {
      return o2.setHeader("Set-Cookie", b);
    }, w = function(b, m) {
      if (!m) return b;
      try {
        return JSON.parse(b);
      } catch {
        return b;
      }
    }, $ = {
      parseJSON: i,
      set: function() {
        var b = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : "", m = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : "", y = arguments.length > 2 && arguments[2] !== void 0 ? arguments[2] : {
          path: "/"
        };
        if (!u) if (m = (m === void 0 ? "undefined" : a(m)) === "object" ? JSON.stringify(m) : m, c) {
          var S = p();
          S.push(s.serialize(b, m, y)), v(S);
        } else document.cookie = s.serialize(b, m, y);
      },
      setAll: function() {
        var b = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : [];
        u || Array.isArray(b) && b.forEach(function(m) {
          var y = m.name, S = y === void 0 ? "" : y, d = m.value, f = d === void 0 ? "" : d, g = m.opts, k = g === void 0 ? {
            path: "/"
          } : g;
          $.set(S, f, k);
        });
      },
      get: function() {
        var b = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : "", m = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : {
          fromRes: false,
          parseJSON: $.parseJSON
        };
        if (u) return "";
        var y = s.parse(h(m.fromRes)), S = y[b];
        return w(S, m.parseJSON);
      },
      getAll: function() {
        var b = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : {
          fromRes: false,
          parseJSON: $.parseJSON
        };
        if (u) return {};
        var m = s.parse(h(b.fromRes));
        for (var y in m) m[y] = w(m[y], b.parseJSON);
        return m;
      },
      remove: function() {
        var b = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : "", m = arguments.length > 1 && arguments[1] !== void 0 ? arguments[1] : {
          path: "/"
        };
        u || (m.expires = /* @__PURE__ */ new Date(0), $.set(b, "", m));
      },
      removeAll: function() {
        var b = arguments.length > 0 && arguments[0] !== void 0 ? arguments[0] : {
          path: "/"
        };
        if (!u) {
          var m = s.parse(h());
          for (var y in m) $.remove(y, b);
        }
      },
      nodeCookie: s
    };
    return $;
  };
}, function(e, t, n) {
  function a(u, h) {
    if (typeof u != "string") throw new TypeError("argument str must be a string");
    for (var p = {}, v = h || {}, w = u.split(l), $ = v.decode || o2, b = 0; b < w.length; b++) {
      var m = w[b], y = m.indexOf("=");
      if (!(y < 0)) {
        var S = m.substr(0, y).trim(), d = m.substr(++y, m.length).trim();
        d[0] == '"' && (d = d.slice(1, -1)), p[S] == null && (p[S] = r(d, $));
      }
    }
    return p;
  }
  function s(u, h, p) {
    var v = p || {}, w = v.encode || i;
    if (typeof w != "function") throw new TypeError("option encode is invalid");
    if (!c.test(u)) throw new TypeError("argument name is invalid");
    var $ = w(h);
    if ($ && !c.test($)) throw new TypeError("argument val is invalid");
    var b = u + "=" + $;
    if (v.maxAge != null) {
      var m = v.maxAge - 0;
      if (isNaN(m)) throw new Error("maxAge should be a Number");
      b += "; Max-Age=" + Math.floor(m);
    }
    if (v.domain) {
      if (!c.test(v.domain)) throw new TypeError("option domain is invalid");
      b += "; Domain=" + v.domain;
    }
    if (v.path) {
      if (!c.test(v.path)) throw new TypeError("option path is invalid");
      b += "; Path=" + v.path;
    }
    if (v.expires) {
      if (typeof v.expires.toUTCString != "function") throw new TypeError("option expires is invalid");
      b += "; Expires=" + v.expires.toUTCString();
    }
    if (v.httpOnly && (b += "; HttpOnly"), v.secure && (b += "; Secure"), v.sameSite) switch (typeof v.sameSite == "string" ? v.sameSite.toLowerCase() : v.sameSite) {
      case true:
        b += "; SameSite=Strict";
        break;
      case "lax":
        b += "; SameSite=Lax";
        break;
      case "strict":
        b += "; SameSite=Strict";
        break;
      case "none":
        b += "; SameSite=None";
        break;
      default:
        throw new TypeError("option sameSite is invalid");
    }
    return b;
  }
  function r(u, h) {
    try {
      return h(u);
    } catch {
      return u;
    }
  }
  t.parse = a, t.serialize = s;
  var o2 = decodeURIComponent, i = encodeURIComponent, l = /; */, c = /^[\u0009\u0020-\u007e\u0080-\u00ff]+$/;
}]);
var Lh = new Uint8Array(16);
var Ye = [];
for (let e = 0; e < 256; ++e) Ye.push((e + 256).toString(16).slice(1));
var Ah = typeof crypto < "u" && crypto.randomUUID && crypto.randomUUID.bind(crypto);
var pl = {
  exports: {}
};
(function(e) {
  var t = Object.prototype.hasOwnProperty, n = "~";
  function a() {
  }
  Object.create && (a.prototype = /* @__PURE__ */ Object.create(null), new a().__proto__ || (n = false));
  function s(l, c, u) {
    this.fn = l, this.context = c, this.once = u || false;
  }
  function r(l, c, u, h, p) {
    if (typeof u != "function") throw new TypeError("The listener must be a function");
    var v = new s(u, h || l, p), w = n ? n + c : c;
    return l._events[w] ? l._events[w].fn ? l._events[w] = [l._events[w], v] : l._events[w].push(v) : (l._events[w] = v, l._eventsCount++), l;
  }
  function o2(l, c) {
    --l._eventsCount === 0 ? l._events = new a() : delete l._events[c];
  }
  function i() {
    this._events = new a(), this._eventsCount = 0;
  }
  i.prototype.eventNames = function() {
    var c = [], u, h;
    if (this._eventsCount === 0) return c;
    for (h in u = this._events) t.call(u, h) && c.push(n ? h.slice(1) : h);
    return Object.getOwnPropertySymbols ? c.concat(Object.getOwnPropertySymbols(u)) : c;
  }, i.prototype.listeners = function(c) {
    var u = n ? n + c : c, h = this._events[u];
    if (!h) return [];
    if (h.fn) return [h.fn];
    for (var p = 0, v = h.length, w = new Array(v); p < v; p++) w[p] = h[p].fn;
    return w;
  }, i.prototype.listenerCount = function(c) {
    var u = n ? n + c : c, h = this._events[u];
    return h ? h.fn ? 1 : h.length : 0;
  }, i.prototype.emit = function(c, u, h, p, v, w) {
    var $ = n ? n + c : c;
    if (!this._events[$]) return false;
    var b = this._events[$], m = arguments.length, y, S;
    if (b.fn) {
      switch (b.once && this.removeListener(c, b.fn, void 0, true), m) {
        case 1:
          return b.fn.call(b.context), true;
        case 2:
          return b.fn.call(b.context, u), true;
        case 3:
          return b.fn.call(b.context, u, h), true;
        case 4:
          return b.fn.call(b.context, u, h, p), true;
        case 5:
          return b.fn.call(b.context, u, h, p, v), true;
        case 6:
          return b.fn.call(b.context, u, h, p, v, w), true;
      }
      for (S = 1, y = new Array(m - 1); S < m; S++) y[S - 1] = arguments[S];
      b.fn.apply(b.context, y);
    } else {
      var d = b.length, f;
      for (S = 0; S < d; S++) switch (b[S].once && this.removeListener(c, b[S].fn, void 0, true), m) {
        case 1:
          b[S].fn.call(b[S].context);
          break;
        case 2:
          b[S].fn.call(b[S].context, u);
          break;
        case 3:
          b[S].fn.call(b[S].context, u, h);
          break;
        case 4:
          b[S].fn.call(b[S].context, u, h, p);
          break;
        default:
          if (!y) for (f = 1, y = new Array(m - 1); f < m; f++) y[f - 1] = arguments[f];
          b[S].fn.apply(b[S].context, y);
      }
    }
    return true;
  }, i.prototype.on = function(c, u, h) {
    return r(this, c, u, h, false);
  }, i.prototype.once = function(c, u, h) {
    return r(this, c, u, h, true);
  }, i.prototype.removeListener = function(c, u, h, p) {
    var v = n ? n + c : c;
    if (!this._events[v]) return this;
    if (!u) return o2(this, v), this;
    var w = this._events[v];
    if (w.fn) w.fn === u && (!p || w.once) && (!h || w.context === h) && o2(this, v);
    else {
      for (var $ = 0, b = [], m = w.length; $ < m; $++) (w[$].fn !== u || p && !w[$].once || h && w[$].context !== h) && b.push(w[$]);
      b.length ? this._events[v] = b.length === 1 ? b[0] : b : o2(this, v);
    }
    return this;
  }, i.prototype.removeAllListeners = function(c) {
    var u;
    return c ? (u = n ? n + c : c, this._events[u] && o2(this, u)) : (this._events = new a(), this._eventsCount = 0), this;
  }, i.prototype.off = i.prototype.removeListener, i.prototype.addListener = i.prototype.on, i.prefixed = n, i.EventEmitter = i, e.exports = i;
})(pl);
var Ph = pl.exports;
var Mh = Object.defineProperty;
var Wr = Math.pow;
var Rh = (e, t, n) => t in e ? Mh(e, t, {
  enumerable: true,
  configurable: true,
  writable: true,
  value: n
}) : e[t] = n;
var Fh = (e, t, n) => (Rh(e, t + "", n), n);
var so = ((e) => (e[e.GT = 1] = "GT", e[e.GTE = 2] = "GTE", e[e.LT = 3] = "LT", e[e.LTE = 4] = "LTE", e))(so || {});
function gl(e) {
  return Object.entries(e).forEach(([t, n]) => {
    if (n && typeof n == "object") {
      if (n instanceof Array && n.length === 0) return n;
      gl(n);
    }
    (n && typeof n == "object" && !Object.keys(n).length || n === null || n === void 0 || typeof n == "number" && isNaN(n)) && (Array.isArray(e) ? e.splice(+t, 1) : delete e[t]);
  }), e;
}
var zr;
var Gr;
var Yr;
var Zr;
var Kr;
var qr;
var Xr = ((zr = typeof globalThis < "u" ? globalThis : void 0) == null ? void 0 : zr.crypto) || ((Gr = typeof global < "u" ? global : void 0) == null ? void 0 : Gr.crypto) || ((Yr = typeof window < "u" ? window : void 0) == null ? void 0 : Yr.crypto) || ((Zr = typeof self < "u" ? self : void 0) == null ? void 0 : Zr.crypto) || ((qr = (Kr = typeof frames < "u" ? frames : void 0) == null ? void 0 : Kr[0]) == null ? void 0 : qr.crypto);
var oo;
Xr ? oo = (e) => {
  const t = [];
  for (let n = 0, a; n < e; n += 4) t.push(Xr.getRandomValues(new Uint32Array(1))[0]);
  return new xt(t, e);
} : oo = (e) => {
  const t = [], n = (a) => {
    let s = a, r = 987654321;
    const o2 = 4294967295;
    return () => {
      r = 36969 * (r & 65535) + (r >> 16) & o2, s = 18e3 * (s & 65535) + (s >> 16) & o2;
      let i = (r << 16) + s & o2;
      return i /= 4294967296, i += 0.5, i * (Math.random() > 0.5 ? 1 : -1);
    };
  };
  for (let a = 0, s; a < e; a += 4) {
    const r = n((s || Math.random()) * 4294967296);
    s = r() * 987654071, t.push(r() * 4294967296 | 0);
  }
  return new xt(t, e);
};
var Ja = class {
  static create(...e) {
    return new this(...e);
  }
  mixIn(e) {
    return Object.assign(this, e);
  }
  clone() {
    const e = new this.constructor();
    return Object.assign(e, this), e;
  }
};
var xt = class extends Ja {
  constructor(e = [], t = e.length * 4) {
    super();
    let n = e;
    if (n instanceof ArrayBuffer && (n = new Uint8Array(n)), (n instanceof Int8Array || n instanceof Uint8ClampedArray || n instanceof Int16Array || n instanceof Uint16Array || n instanceof Int32Array || n instanceof Uint32Array || n instanceof Float32Array || n instanceof Float64Array) && (n = new Uint8Array(n.buffer, n.byteOffset, n.byteLength)), n instanceof Uint8Array) {
      const a = n.byteLength, s = [];
      for (let r = 0; r < a; r += 1) s[r >>> 2] |= n[r] << 24 - r % 4 * 8;
      this.words = s, this.sigBytes = a;
    } else this.words = e, this.sigBytes = t;
  }
  toString(e = Vh) {
    return e.stringify(this);
  }
  concat(e) {
    const t = this.words, n = e.words, a = this.sigBytes, s = e.sigBytes;
    if (this.clamp(), a % 4) for (let r = 0; r < s; r += 1) {
      const o2 = n[r >>> 2] >>> 24 - r % 4 * 8 & 255;
      t[a + r >>> 2] |= o2 << 24 - (a + r) % 4 * 8;
    }
    else for (let r = 0; r < s; r += 4) t[a + r >>> 2] = n[r >>> 2];
    return this.sigBytes += s, this;
  }
  clamp() {
    const {
      words: e,
      sigBytes: t
    } = this;
    e[t >>> 2] &= 4294967295 << 32 - t % 4 * 8, e.length = Math.ceil(t / 4);
  }
  clone() {
    const e = super.clone.call(this);
    return e.words = this.words.slice(0), e;
  }
};
Fh(xt, "random", oo);
var Vh = {
  stringify(e) {
    const {
      words: t,
      sigBytes: n
    } = e, a = [];
    for (let s = 0; s < n; s += 1) {
      const r = t[s >>> 2] >>> 24 - s % 4 * 8 & 255;
      a.push((r >>> 4).toString(16)), a.push((r & 15).toString(16));
    }
    return a.join("");
  },
  parse(e) {
    const t = e.length, n = [];
    for (let a = 0; a < t; a += 2) n[a >>> 3] |= parseInt(e.substr(a, 2), 16) << 24 - a % 8 * 4;
    return new xt(n, t / 2);
  }
};
var Jr = {
  stringify(e) {
    const {
      words: t,
      sigBytes: n
    } = e, a = [];
    for (let s = 0; s < n; s += 1) {
      const r = t[s >>> 2] >>> 24 - s % 4 * 8 & 255;
      a.push(String.fromCharCode(r));
    }
    return a.join("");
  },
  parse(e) {
    const t = e.length, n = [];
    for (let a = 0; a < t; a += 1) n[a >>> 2] |= (e.charCodeAt(a) & 255) << 24 - a % 4 * 8;
    return new xt(n, t);
  }
};
var Ba = {
  stringify(e) {
    try {
      return decodeURIComponent(escape(Jr.stringify(e)));
    } catch {
      throw new Error("Malformed UTF-8 data");
    }
  },
  parse(e) {
    return Jr.parse(unescape(encodeURIComponent(e)));
  }
};
var Uh = class extends Ja {
  constructor() {
    super(), this._minBufferSize = 0;
  }
  reset() {
    this._data = new xt(), this._nDataBytes = 0;
  }
  _append(e) {
    let t = e;
    typeof t == "string" && (t = Ba.parse(t)), this._data.concat(t), this._nDataBytes += t.sigBytes;
  }
  _process(e) {
    let t;
    const {
      _data: n,
      blockSize: a
    } = this, s = n.words, r = n.sigBytes, o2 = a * 4;
    let i = r / o2;
    e ? i = Math.ceil(i) : i = Math.max((i | 0) - this._minBufferSize, 0);
    const l = i * a, c = Math.min(l * 4, r);
    if (l) {
      for (let u = 0; u < l; u += a) this._doProcessBlock(s, u);
      t = s.splice(0, l), n.sigBytes -= c;
    }
    return new xt(t, c);
  }
  clone() {
    const e = super.clone.call(this);
    return e._data = this._data.clone(), e;
  }
};
var Qa = class extends Uh {
  constructor(e) {
    super(), this.blockSize = 512 / 32, this.cfg = Object.assign(new Ja(), e), this.reset();
  }
  static _createHelper(e) {
    return (t, n) => new e(n).finalize(t);
  }
  static _createHmacHelper(e) {
    return (t, n) => new Wh(e, n).finalize(t);
  }
  reset() {
    super.reset.call(this), this._doReset();
  }
  update(e) {
    return this._append(e), this._process(), this;
  }
  finalize(e) {
    return e && this._append(e), this._doFinalize();
  }
};
var Wh = class extends Ja {
  constructor(e, t) {
    super();
    const n = new e();
    this._hasher = n;
    let a = t;
    typeof a == "string" && (a = Ba.parse(a));
    const s = n.blockSize, r = s * 4;
    a.sigBytes > r && (a = n.finalize(t)), a.clamp();
    const o2 = a.clone();
    this._oKey = o2;
    const i = a.clone();
    this._iKey = i;
    const l = o2.words, c = i.words;
    for (let u = 0; u < s; u += 1) l[u] ^= 1549556828, c[u] ^= 909522486;
    o2.sigBytes = r, i.sigBytes = r, this.reset();
  }
  reset() {
    const e = this._hasher;
    e.reset(), e.update(this._iKey);
  }
  update(e) {
    return this._hasher.update(e), this;
  }
  finalize(e) {
    const t = this._hasher, n = t.finalize(e);
    return t.reset(), t.finalize(this._oKey.clone().concat(n));
  }
};
var vl = [];
var bl = [];
var Hh = (e) => {
  const t = Math.sqrt(e);
  for (let n = 2; n <= t; n += 1) if (!(e % n)) return false;
  return true;
};
var Qr = (e) => (e - (e | 0)) * 4294967296 | 0;
var Ta = 2;
var xn = 0;
for (; xn < 64; ) Hh(Ta) && (xn < 8 && (vl[xn] = Qr(Wr(Ta, 1 / 2))), bl[xn] = Qr(Wr(Ta, 1 / 3)), xn += 1), Ta += 1;
var en = [];
var zh = class extends Qa {
  _doReset() {
    this._hash = new xt(vl.slice(0));
  }
  _doProcessBlock(e, t) {
    const n = this._hash.words;
    let a = n[0], s = n[1], r = n[2], o2 = n[3], i = n[4], l = n[5], c = n[6], u = n[7];
    for (let h = 0; h < 64; h += 1) {
      if (h < 16) en[h] = e[t + h] | 0;
      else {
        const y = en[h - 15], S = (y << 25 | y >>> 7) ^ (y << 14 | y >>> 18) ^ y >>> 3, d = en[h - 2], f = (d << 15 | d >>> 17) ^ (d << 13 | d >>> 19) ^ d >>> 10;
        en[h] = S + en[h - 7] + f + en[h - 16];
      }
      const p = i & l ^ ~i & c, v = a & s ^ a & r ^ s & r, w = (a << 30 | a >>> 2) ^ (a << 19 | a >>> 13) ^ (a << 10 | a >>> 22), $ = (i << 26 | i >>> 6) ^ (i << 21 | i >>> 11) ^ (i << 7 | i >>> 25), b = u + $ + p + bl[h] + en[h], m = w + v;
      u = c, c = l, l = i, i = o2 + b | 0, o2 = r, r = s, s = a, a = b + m | 0;
    }
    n[0] = n[0] + a | 0, n[1] = n[1] + s | 0, n[2] = n[2] + r | 0, n[3] = n[3] + o2 | 0, n[4] = n[4] + i | 0, n[5] = n[5] + l | 0, n[6] = n[6] + c | 0, n[7] = n[7] + u | 0;
  }
  _doFinalize() {
    const e = this._data, t = e.words, n = this._nDataBytes * 8, a = e.sigBytes * 8;
    return t[a >>> 5] |= 128 << 24 - a % 32, t[(a + 64 >>> 9 << 4) + 14] = Math.floor(n / 4294967296), t[(a + 64 >>> 9 << 4) + 15] = n, e.sigBytes = t.length * 4, this._process(), this._hash;
  }
  clone() {
    const e = super.clone.call(this);
    return e._hash = this._hash.clone(), e;
  }
};
var Gh = Qa._createHelper(zh);
function Yh(e, t = true) {
  const n = Gh(e).toString();
  return t ? n.toUpperCase() : n;
}
var ws = {
  p1: "95d65c73dc5c437",
  p2: "0ae9018fb7",
  p3: "f2eab69"
};
var yl = (e) => (Object.keys(e).forEach((t) => {
  typeof e[t] == "object" && (e[t] = yl(e[t])), (typeof e[t] == "number" || typeof e[t] == "boolean") && (typeof e[t] == "number" ? e[t] = e[t].toString().toUpperCase() : e[t] = e[t].toString());
}), e);
var Zh = (e) => {
  const {
    timestamp: t,
    traceId: n,
    deviceId: a,
    platformId: s,
    appVersion: r,
    requestPayload: o2
  } = e;
  let i = "{}";
  const l = o2 ? JSON.parse(JSON.stringify(o2)) : {};
  if (l && typeof l == "object" && JSON.stringify(l) !== "{}") {
    const u = yl(gl(l));
    i = JSON.stringify(u);
  }
  return `${`${ws.p1}${ws.p2}${ws.p3}`}${t}${n}${a}${s}${r}${i}`;
};
export default function cC(e) {
  const t = Zh(e);
  return {
    encryptionContent: t,
    sign: Yh(t, true)
  };
}
var Y = [];
for (let e = 0; e < 64; e += 1) Y[e] = Math.abs(Math.sin(e + 1)) * 4294967296 | 0;
var Xe = (e, t, n, a, s, r, o2) => {
  const i = e + (t & n | ~t & a) + s + o2;
  return (i << r | i >>> 32 - r) + t;
};
var Je = (e, t, n, a, s, r, o2) => {
  const i = e + (t & a | n & ~a) + s + o2;
  return (i << r | i >>> 32 - r) + t;
};
var Qe = (e, t, n, a, s, r, o2) => {
  const i = e + (t ^ n ^ a) + s + o2;
  return (i << r | i >>> 32 - r) + t;
};
var et = (e, t, n, a, s, r, o2) => {
  const i = e + (n ^ (t | ~a)) + s + o2;
  return (i << r | i >>> 32 - r) + t;
};
var qh = class extends Qa {
  _doReset() {
    this._hash = new xt([1732584193, 4023233417, 2562383102, 271733878]);
  }
  _doProcessBlock(e, t) {
    const n = e;
    for (let M = 0; M < 16; M += 1) {
      const A = t + M, I = e[A];
      n[A] = (I << 8 | I >>> 24) & 16711935 | (I << 24 | I >>> 8) & 4278255360;
    }
    const a = this._hash.words, s = n[t + 0], r = n[t + 1], o2 = n[t + 2], i = n[t + 3], l = n[t + 4], c = n[t + 5], u = n[t + 6], h = n[t + 7], p = n[t + 8], v = n[t + 9], w = n[t + 10], $ = n[t + 11], b = n[t + 12], m = n[t + 13], y = n[t + 14], S = n[t + 15];
    let d = a[0], f = a[1], g = a[2], k = a[3];
    d = Xe(d, f, g, k, s, 7, Y[0]), k = Xe(k, d, f, g, r, 12, Y[1]), g = Xe(g, k, d, f, o2, 17, Y[2]), f = Xe(f, g, k, d, i, 22, Y[3]), d = Xe(d, f, g, k, l, 7, Y[4]), k = Xe(k, d, f, g, c, 12, Y[5]), g = Xe(g, k, d, f, u, 17, Y[6]), f = Xe(f, g, k, d, h, 22, Y[7]), d = Xe(d, f, g, k, p, 7, Y[8]), k = Xe(k, d, f, g, v, 12, Y[9]), g = Xe(g, k, d, f, w, 17, Y[10]), f = Xe(f, g, k, d, $, 22, Y[11]), d = Xe(d, f, g, k, b, 7, Y[12]), k = Xe(k, d, f, g, m, 12, Y[13]), g = Xe(g, k, d, f, y, 17, Y[14]), f = Xe(f, g, k, d, S, 22, Y[15]), d = Je(d, f, g, k, r, 5, Y[16]), k = Je(k, d, f, g, u, 9, Y[17]), g = Je(g, k, d, f, $, 14, Y[18]), f = Je(f, g, k, d, s, 20, Y[19]), d = Je(d, f, g, k, c, 5, Y[20]), k = Je(k, d, f, g, w, 9, Y[21]), g = Je(g, k, d, f, S, 14, Y[22]), f = Je(f, g, k, d, l, 20, Y[23]), d = Je(d, f, g, k, v, 5, Y[24]), k = Je(k, d, f, g, y, 9, Y[25]), g = Je(g, k, d, f, i, 14, Y[26]), f = Je(f, g, k, d, p, 20, Y[27]), d = Je(d, f, g, k, m, 5, Y[28]), k = Je(k, d, f, g, o2, 9, Y[29]), g = Je(g, k, d, f, h, 14, Y[30]), f = Je(f, g, k, d, b, 20, Y[31]), d = Qe(d, f, g, k, c, 4, Y[32]), k = Qe(k, d, f, g, p, 11, Y[33]), g = Qe(g, k, d, f, $, 16, Y[34]), f = Qe(f, g, k, d, y, 23, Y[35]), d = Qe(d, f, g, k, r, 4, Y[36]), k = Qe(k, d, f, g, l, 11, Y[37]), g = Qe(g, k, d, f, h, 16, Y[38]), f = Qe(f, g, k, d, w, 23, Y[39]), d = Qe(d, f, g, k, m, 4, Y[40]), k = Qe(k, d, f, g, s, 11, Y[41]), g = Qe(g, k, d, f, i, 16, Y[42]), f = Qe(f, g, k, d, u, 23, Y[43]), d = Qe(d, f, g, k, v, 4, Y[44]), k = Qe(k, d, f, g, b, 11, Y[45]), g = Qe(g, k, d, f, S, 16, Y[46]), f = Qe(f, g, k, d, o2, 23, Y[47]), d = et(d, f, g, k, s, 6, Y[48]), k = et(k, d, f, g, h, 10, Y[49]), g = et(g, k, d, f, y, 15, Y[50]), f = et(f, g, k, d, c, 21, Y[51]), d = et(d, f, g, k, b, 6, Y[52]), k = et(k, d, f, g, i, 10, Y[53]), g = et(g, k, d, f, w, 15, Y[54]), f = et(f, g, k, d, r, 21, Y[55]), d = et(d, f, g, k, p, 6, Y[56]), k = et(k, d, f, g, S, 10, Y[57]), g = et(g, k, d, f, u, 15, Y[58]), f = et(f, g, k, d, m, 21, Y[59]), d = et(d, f, g, k, l, 6, Y[60]), k = et(k, d, f, g, $, 10, Y[61]), g = et(g, k, d, f, o2, 15, Y[62]), f = et(f, g, k, d, v, 21, Y[63]), a[0] = a[0] + d | 0, a[1] = a[1] + f | 0, a[2] = a[2] + g | 0, a[3] = a[3] + k | 0;
  }
  _doFinalize() {
    const e = this._data, t = e.words, n = this._nDataBytes * 8, a = e.sigBytes * 8;
    t[a >>> 5] |= 128 << 24 - a % 32;
    const s = Math.floor(n / 4294967296), r = n;
    t[(a + 64 >>> 9 << 4) + 15] = (s << 8 | s >>> 24) & 16711935 | (s << 24 | s >>> 8) & 4278255360, t[(a + 64 >>> 9 << 4) + 14] = (r << 8 | r >>> 24) & 16711935 | (r << 24 | r >>> 8) & 4278255360, e.sigBytes = (t.length + 1) * 4, this._process();
    const o2 = this._hash, i = o2.words;
    for (let l = 0; l < 4; l += 1) {
      const c = i[l];
      i[l] = (c << 8 | c >>> 24) & 16711935 | (c << 24 | c >>> 8) & 4278255360;
    }
    return o2;
  }
  clone() {
    const e = super.clone.call(this);
    return e._hash = this._hash.clone(), e;
  }
};
var Xh = Qa._createHelper(qh);
function Jh(e, t) {
  const n = Object.assign({}, e);
  for (let a = 0; a < t.length; a += 1) {
    const s = t[a];
    delete n[s];
  }
  return n;
}
var ia = Jh;
var oi = 0;
var ri = "webkit moz ms o".split(" ");
var Mt;
var Rt;
var _1 = typeof window > "u";
if (_1) Mt = function() {
}, Rt = function() {
};
else {
  Mt = window.requestAnimationFrame, Rt = window.cancelAnimationFrame;
  let e;
  for (let t = 0; t < ri.length && !(Mt && Rt); t++) e = ri[t], Mt = Mt || window[e + "RequestAnimationFrame"], Rt = Rt || window[e + "CancelAnimationFrame"] || window[e + "CancelRequestAnimationFrame"];
  (!Mt || !Rt) && (Mt = function(t) {
    const n = (/* @__PURE__ */ new Date()).getTime(), a = Math.max(0, 16 - (n - oi)), s = window.setTimeout(() => {
      t(n + a);
    }, a);
    return oi = n + a, s;
  }, Rt = function(t) {
    window.clearTimeout(t);
  });
}
var E1 = (e, t) => {
  const n = e.__vccOpts || e;
  for (const [a, s] of t) n[a] = s;
  return n;
};
var L1 = {
  props: {
    startVal: {
      type: Number,
      required: false,
      default: 0
    },
    endVal: {
      type: Number,
      required: false,
      default: 2017
    },
    duration: {
      type: Number,
      required: false,
      default: 3e3
    },
    autoplay: {
      type: Boolean,
      required: false,
      default: true
    },
    decimals: {
      type: Number,
      required: false,
      default: 0,
      validator(e) {
        return e >= 0;
      }
    },
    decimal: {
      type: String,
      required: false,
      default: "."
    },
    separator: {
      type: String,
      required: false,
      default: ","
    },
    prefix: {
      type: String,
      required: false,
      default: ""
    },
    suffix: {
      type: String,
      required: false,
      default: ""
    },
    useEasing: {
      type: Boolean,
      required: false,
      default: true
    },
    easingFn: {
      type: Function,
      default(e, t, n, a) {
        return n * (-Math.pow(2, -10 * e / a) + 1) * 1024 / 1023 + t;
      }
    }
  },
  data() {
    return {
      localStartVal: this.startVal,
      displayValue: this.formatNumber(this.startVal),
      printVal: null,
      paused: false,
      localDuration: this.duration,
      startTime: null,
      timestamp: null,
      remaining: null,
      rAF: null
    };
  },
  computed: {
    countDown() {
      return this.startVal > this.endVal;
    }
  },
  watch: {
    startVal() {
      this.autoplay && this.start();
    },
    endVal() {
      this.autoplay && this.start();
    }
  },
  mounted() {
    this.autoplay && this.start(), this.$emit("mountedCallback");
  },
  methods: {
    start() {
      this.localStartVal = this.startVal, this.startTime = null, this.localDuration = this.duration, this.paused = false, this.rAF = Mt(this.count);
    },
    pauseResume() {
      this.paused ? (this.resume(), this.paused = false) : (this.pause(), this.paused = true);
    },
    pause() {
      Rt(this.rAF);
    },
    resume() {
      this.startTime = null, this.localDuration = +this.remaining, this.localStartVal = +this.printVal, Mt(this.count);
    },
    reset() {
      this.startTime = null, Rt(this.rAF), this.displayValue = this.formatNumber(this.startVal);
    },
    count(e) {
      this.startTime || (this.startTime = e), this.timestamp = e;
      const t = e - this.startTime;
      this.remaining = this.localDuration - t, this.useEasing ? this.countDown ? this.printVal = this.localStartVal - this.easingFn(t, 0, this.localStartVal - this.endVal, this.localDuration) : this.printVal = this.easingFn(t, this.localStartVal, this.endVal - this.localStartVal, this.localDuration) : this.countDown ? this.printVal = this.localStartVal - (this.localStartVal - this.endVal) * (t / this.localDuration) : this.printVal = this.localStartVal + (this.endVal - this.localStartVal) * (t / this.localDuration), this.countDown ? this.printVal = this.printVal < this.endVal ? this.endVal : this.printVal : this.printVal = this.printVal > this.endVal ? this.endVal : this.printVal, this.displayValue = this.formatNumber(this.printVal), t < this.localDuration ? this.rAF = Mt(this.count) : this.$emit("callback");
    },
    isNumber(e) {
      return !isNaN(parseFloat(e));
    },
    formatNumber(e) {
      e = e.toFixed(this.decimals), e += "";
      const t = e.split(".");
      let n = t[0];
      const a = t.length > 1 ? this.decimal + t[1] : "", s = /(\d+)(\d{3})/;
      if (this.separator && !this.isNumber(this.separator)) for (; s.test(n); ) n = n.replace(s, "$1" + this.separator + "$2");
      return this.prefix + n + a + this.suffix;
    }
  },
  destroyed() {
    Rt(this.rAF);
  }
};
function O1(e, t, n, a, s, r) {
  return E(), O("span", null, ee(s.displayValue), 1);
}
var Ia = E1(L1, [["render", O1]]);
function I1(e, t, n) {
  return t in e ? Object.defineProperty(e, t, {
    value: n,
    enumerable: true,
    configurable: true,
    writable: true
  }) : e[t] = n, e;
}
function ii(e, t) {
  var n = Object.keys(e);
  if (Object.getOwnPropertySymbols) {
    var a = Object.getOwnPropertySymbols(e);
    t && (a = a.filter(function(s) {
      return Object.getOwnPropertyDescriptor(e, s).enumerable;
    })), n.push.apply(n, a);
  }
  return n;
}
Ia.unmounted = Ia.destroyed, Reflect.deleteProperty(Ia, "destroyed");
(function(e) {
  for (var t = 1; t < arguments.length; t++) {
    var n = arguments[t] != null ? arguments[t] : {};
    t % 2 ? ii(Object(n), true).forEach(function(a) {
      I1(e, a, n[a]);
    }) : Object.getOwnPropertyDescriptors ? Object.defineProperties(e, Object.getOwnPropertyDescriptors(n)) : ii(Object(n)).forEach(function(a) {
      Object.defineProperty(e, a, Object.getOwnPropertyDescriptor(n, a));
    });
  }
  return e;
})({
  name: "CountTo",
  emits: ["callback", "mountedCallback"]
}, Ia);
var Ie = ((e) => (e.Light = "light", e.Dark = "dark", e))(Ie || {});
function Sn() {
  return typeof window > "u";
}
var pt = "top";
var St = "bottom";
var Ct = "right";
var mt = "left";
var To = "auto";
var ca = [pt, St, Ct, mt];
var Cn = "start";
var aa = "end";
var $p = "clippingParents";
var _l = "viewport";
var Vn = "popper";
var Dp = "reference";
var li = ca.reduce(function(e, t) {
  return e.concat([t + "-" + Cn, t + "-" + aa]);
}, []);
var El = [].concat(ca, [To]).reduce(function(e, t) {
  return e.concat([t, t + "-" + Cn, t + "-" + aa]);
}, []);
var wp = "beforeRead";
var kp = "read";
var Sp = "afterRead";
var Cp = "beforeMain";
var Tp = "main";
var _p = "afterMain";
var Ep = "beforeWrite";
var Lp = "write";
var Op = "afterWrite";
var Ip = [wp, kp, Sp, Cp, Tp, _p, Ep, Lp, Op];
function jt(e) {
  return e ? (e.nodeName || "").toLowerCase() : null;
}
function Et(e) {
  if (e == null) return window;
  if (e.toString() !== "[object Window]") {
    var t = e.ownerDocument;
    return t && t.defaultView || window;
  }
  return e;
}
function an(e) {
  var t = Et(e).Element;
  return e instanceof t || e instanceof Element;
}
function Dt(e) {
  var t = Et(e).HTMLElement;
  return e instanceof t || e instanceof HTMLElement;
}
function _o(e) {
  if (typeof ShadowRoot > "u") return false;
  var t = Et(e).ShadowRoot;
  return e instanceof t || e instanceof ShadowRoot;
}
function Ap(e) {
  var t = e.state;
  Object.keys(t.elements).forEach(function(n) {
    var a = t.styles[n] || {}, s = t.attributes[n] || {}, r = t.elements[n];
    !Dt(r) || !jt(r) || (Object.assign(r.style, a), Object.keys(s).forEach(function(o2) {
      var i = s[o2];
      i === false ? r.removeAttribute(o2) : r.setAttribute(o2, i === true ? "" : i);
    }));
  });
}
function Pp(e) {
  var t = e.state, n = {
    popper: {
      position: t.options.strategy,
      left: "0",
      top: "0",
      margin: "0"
    },
    arrow: {
      position: "absolute"
    },
    reference: {}
  };
  return Object.assign(t.elements.popper.style, n.popper), t.styles = n, t.elements.arrow && Object.assign(t.elements.arrow.style, n.arrow), function() {
    Object.keys(t.elements).forEach(function(a) {
      var s = t.elements[a], r = t.attributes[a] || {}, o2 = Object.keys(t.styles.hasOwnProperty(a) ? t.styles[a] : n[a]), i = o2.reduce(function(l, c) {
        return l[c] = "", l;
      }, {});
      !Dt(s) || !jt(s) || (Object.assign(s.style, i), Object.keys(r).forEach(function(l) {
        s.removeAttribute(l);
      }));
    });
  };
}
var Np = {
  name: "applyStyles",
  enabled: true,
  phase: "write",
  fn: Ap,
  effect: Pp,
  requires: ["computeStyles"]
};
function Bt(e) {
  return e.split("-")[0];
}
var tn = Math.max;
var xa = Math.min;
var Tn = Math.round;
function io() {
  var e = navigator.userAgentData;
  return e != null && e.brands ? e.brands.map(function(t) {
    return t.brand + "/" + t.version;
  }).join(" ") : navigator.userAgent;
}
function Ll() {
  return !/^((?!chrome|android).)*safari/i.test(io());
}
function _n(e, t, n) {
  t === void 0 && (t = false), n === void 0 && (n = false);
  var a = e.getBoundingClientRect(), s = 1, r = 1;
  t && Dt(e) && (s = e.offsetWidth > 0 && Tn(a.width) / e.offsetWidth || 1, r = e.offsetHeight > 0 && Tn(a.height) / e.offsetHeight || 1);
  var o2 = an(e) ? Et(e) : window, i = o2.visualViewport, l = !Ll() && n, c = (a.left + (l && i ? i.offsetLeft : 0)) / s, u = (a.top + (l && i ? i.offsetTop : 0)) / r, h = a.width / s, p = a.height / r;
  return {
    width: h,
    height: p,
    top: u,
    right: c + h,
    bottom: u + p,
    left: c,
    x: c,
    y: u
  };
}
function Eo(e) {
  var t = _n(e), n = e.offsetWidth, a = e.offsetHeight;
  return Math.abs(t.width - n) <= 1 && (n = t.width), Math.abs(t.height - a) <= 1 && (a = t.height), {
    x: e.offsetLeft,
    y: e.offsetTop,
    width: n,
    height: a
  };
}
function Ol(e, t) {
  var n = t.getRootNode && t.getRootNode();
  if (e.contains(t)) return true;
  if (n && _o(n)) {
    var a = t;
    do {
      if (a && e.isSameNode(a)) return true;
      a = a.parentNode || a.host;
    } while (a);
  }
  return false;
}
function Ht(e) {
  return Et(e).getComputedStyle(e);
}
function Mp(e) {
  return ["table", "td", "th"].indexOf(jt(e)) >= 0;
}
function Jt(e) {
  return ((an(e) ? e.ownerDocument : e.document) || window.document).documentElement;
}
function ts(e) {
  return jt(e) === "html" ? e : e.assignedSlot || e.parentNode || (_o(e) ? e.host : null) || Jt(e);
}
function ci(e) {
  return !Dt(e) || Ht(e).position === "fixed" ? null : e.offsetParent;
}
function Rp(e) {
  var t = /firefox/i.test(io()), n = /Trident/i.test(io());
  if (n && Dt(e)) {
    var a = Ht(e);
    if (a.position === "fixed") return null;
  }
  var s = ts(e);
  for (_o(s) && (s = s.host); Dt(s) && ["html", "body"].indexOf(jt(s)) < 0; ) {
    var r = Ht(s);
    if (r.transform !== "none" || r.perspective !== "none" || r.contain === "paint" || ["transform", "perspective"].indexOf(r.willChange) !== -1 || t && r.willChange === "filter" || t && r.filter && r.filter !== "none") return s;
    s = s.parentNode;
  }
  return null;
}
function ua(e) {
  for (var t = Et(e), n = ci(e); n && Mp(n) && Ht(n).position === "static"; ) n = ci(n);
  return n && (jt(n) === "html" || jt(n) === "body" && Ht(n).position === "static") ? t : n || Rp(e) || t;
}
function Lo(e) {
  return ["top", "bottom"].indexOf(e) >= 0 ? "x" : "y";
}
function qn(e, t, n) {
  return tn(e, xa(t, n));
}
function Fp(e, t, n) {
  var a = qn(e, t, n);
  return a > n ? n : a;
}
function Il() {
  return {
    top: 0,
    right: 0,
    bottom: 0,
    left: 0
  };
}
function Al(e) {
  return Object.assign({}, Il(), e);
}
function Pl(e, t) {
  return t.reduce(function(n, a) {
    return n[a] = e, n;
  }, {});
}
var Bp = function(t, n) {
  return t = typeof t == "function" ? t(Object.assign({}, n.rects, {
    placement: n.placement
  })) : t, Al(typeof t != "number" ? t : Pl(t, ca));
};
function xp(e) {
  var t, n = e.state, a = e.name, s = e.options, r = n.elements.arrow, o2 = n.modifiersData.popperOffsets, i = Bt(n.placement), l = Lo(i), c = [mt, Ct].indexOf(i) >= 0, u = c ? "height" : "width";
  if (!(!r || !o2)) {
    var h = Bp(s.padding, n), p = Eo(r), v = l === "y" ? pt : mt, w = l === "y" ? St : Ct, $ = n.rects.reference[u] + n.rects.reference[l] - o2[l] - n.rects.popper[u], b = o2[l] - n.rects.reference[l], m = ua(r), y = m ? l === "y" ? m.clientHeight || 0 : m.clientWidth || 0 : 0, S = $ / 2 - b / 2, d = h[v], f = y - p[u] - h[w], g = y / 2 - p[u] / 2 + S, k = qn(d, g, f), M = l;
    n.modifiersData[a] = (t = {}, t[M] = k, t.centerOffset = k - g, t);
  }
}
function jp(e) {
  var t = e.state, n = e.options, a = n.element, s = a === void 0 ? "[data-popper-arrow]" : a;
  s != null && (typeof s == "string" && (s = t.elements.popper.querySelector(s), !s) || Ol(t.elements.popper, s) && (t.elements.arrow = s));
}
var Vp = {
  name: "arrow",
  enabled: true,
  phase: "main",
  fn: xp,
  effect: jp,
  requires: ["popperOffsets"],
  requiresIfExists: ["preventOverflow"]
};
function En(e) {
  return e.split("-")[1];
}
var Up = {
  top: "auto",
  right: "auto",
  bottom: "auto",
  left: "auto"
};
function Wp(e) {
  var t = e.x, n = e.y, a = window, s = a.devicePixelRatio || 1;
  return {
    x: Tn(t * s) / s || 0,
    y: Tn(n * s) / s || 0
  };
}
function ui(e) {
  var t, n = e.popper, a = e.popperRect, s = e.placement, r = e.variation, o2 = e.offsets, i = e.position, l = e.gpuAcceleration, c = e.adaptive, u = e.roundOffsets, h = e.isFixed, p = o2.x, v = p === void 0 ? 0 : p, w = o2.y, $ = w === void 0 ? 0 : w, b = typeof u == "function" ? u({
    x: v,
    y: $
  }) : {
    x: v,
    y: $
  };
  v = b.x, $ = b.y;
  var m = o2.hasOwnProperty("x"), y = o2.hasOwnProperty("y"), S = mt, d = pt, f = window;
  if (c) {
    var g = ua(n), k = "clientHeight", M = "clientWidth";
    if (g === Et(n) && (g = Jt(n), Ht(g).position !== "static" && i === "absolute" && (k = "scrollHeight", M = "scrollWidth")), g = g, s === pt || (s === mt || s === Ct) && r === aa) {
      d = St;
      var A = h && g === f && f.visualViewport ? f.visualViewport.height : g[k];
      $ -= A - a.height, $ *= l ? 1 : -1;
    }
    if (s === mt || (s === pt || s === St) && r === aa) {
      S = Ct;
      var I = h && g === f && f.visualViewport ? f.visualViewport.width : g[M];
      v -= I - a.width, v *= l ? 1 : -1;
    }
  }
  var oe = Object.assign({
    position: i
  }, c && Up), ce = u === true ? Wp({
    x: v,
    y: $
  }) : {
    x: v,
    y: $
  };
  if (v = ce.x, $ = ce.y, l) {
    var R;
    return Object.assign({}, oe, (R = {}, R[d] = y ? "0" : "", R[S] = m ? "0" : "", R.transform = (f.devicePixelRatio || 1) <= 1 ? "translate(" + v + "px, " + $ + "px)" : "translate3d(" + v + "px, " + $ + "px, 0)", R));
  }
  return Object.assign({}, oe, (t = {}, t[d] = y ? $ + "px" : "", t[S] = m ? v + "px" : "", t.transform = "", t));
}
function Hp(e) {
  var t = e.state, n = e.options, a = n.gpuAcceleration, s = a === void 0 ? true : a, r = n.adaptive, o2 = r === void 0 ? true : r, i = n.roundOffsets, l = i === void 0 ? true : i, c = {
    placement: Bt(t.placement),
    variation: En(t.placement),
    popper: t.elements.popper,
    popperRect: t.rects.popper,
    gpuAcceleration: s,
    isFixed: t.options.strategy === "fixed"
  };
  t.modifiersData.popperOffsets != null && (t.styles.popper = Object.assign({}, t.styles.popper, ui(Object.assign({}, c, {
    offsets: t.modifiersData.popperOffsets,
    position: t.options.strategy,
    adaptive: o2,
    roundOffsets: l
  })))), t.modifiersData.arrow != null && (t.styles.arrow = Object.assign({}, t.styles.arrow, ui(Object.assign({}, c, {
    offsets: t.modifiersData.arrow,
    position: "absolute",
    adaptive: false,
    roundOffsets: l
  })))), t.attributes.popper = Object.assign({}, t.attributes.popper, {
    "data-popper-placement": t.placement
  });
}
var zp = {
  name: "computeStyles",
  enabled: true,
  phase: "beforeWrite",
  fn: Hp,
  data: {}
};
var _a = {
  passive: true
};
function Gp(e) {
  var t = e.state, n = e.instance, a = e.options, s = a.scroll, r = s === void 0 ? true : s, o2 = a.resize, i = o2 === void 0 ? true : o2, l = Et(t.elements.popper), c = [].concat(t.scrollParents.reference, t.scrollParents.popper);
  return r && c.forEach(function(u) {
    u.addEventListener("scroll", n.update, _a);
  }), i && l.addEventListener("resize", n.update, _a), function() {
    r && c.forEach(function(u) {
      u.removeEventListener("scroll", n.update, _a);
    }), i && l.removeEventListener("resize", n.update, _a);
  };
}
var Yp = {
  name: "eventListeners",
  enabled: true,
  phase: "write",
  fn: function() {
  },
  effect: Gp,
  data: {}
};
var Zp = {
  left: "right",
  right: "left",
  bottom: "top",
  top: "bottom"
};
function Aa(e) {
  return e.replace(/left|right|bottom|top/g, function(t) {
    return Zp[t];
  });
}
var Kp = {
  start: "end",
  end: "start"
};
function di(e) {
  return e.replace(/start|end/g, function(t) {
    return Kp[t];
  });
}
function Oo(e) {
  var t = Et(e), n = t.pageXOffset, a = t.pageYOffset;
  return {
    scrollLeft: n,
    scrollTop: a
  };
}
function Io(e) {
  return _n(Jt(e)).left + Oo(e).scrollLeft;
}
function qp(e, t) {
  var n = Et(e), a = Jt(e), s = n.visualViewport, r = a.clientWidth, o2 = a.clientHeight, i = 0, l = 0;
  if (s) {
    r = s.width, o2 = s.height;
    var c = Ll();
    (c || !c && t === "fixed") && (i = s.offsetLeft, l = s.offsetTop);
  }
  return {
    width: r,
    height: o2,
    x: i + Io(e),
    y: l
  };
}
function Xp(e) {
  var t, n = Jt(e), a = Oo(e), s = (t = e.ownerDocument) == null ? void 0 : t.body, r = tn(n.scrollWidth, n.clientWidth, s ? s.scrollWidth : 0, s ? s.clientWidth : 0), o2 = tn(n.scrollHeight, n.clientHeight, s ? s.scrollHeight : 0, s ? s.clientHeight : 0), i = -a.scrollLeft + Io(e), l = -a.scrollTop;
  return Ht(s || n).direction === "rtl" && (i += tn(n.clientWidth, s ? s.clientWidth : 0) - r), {
    width: r,
    height: o2,
    x: i,
    y: l
  };
}
function Ao(e) {
  var t = Ht(e), n = t.overflow, a = t.overflowX, s = t.overflowY;
  return /auto|scroll|overlay|hidden/.test(n + s + a);
}
function Nl(e) {
  return ["html", "body", "#document"].indexOf(jt(e)) >= 0 ? e.ownerDocument.body : Dt(e) && Ao(e) ? e : Nl(ts(e));
}
function Xn(e, t) {
  var n;
  t === void 0 && (t = []);
  var a = Nl(e), s = a === ((n = e.ownerDocument) == null ? void 0 : n.body), r = Et(a), o2 = s ? [r].concat(r.visualViewport || [], Ao(a) ? a : []) : a, i = t.concat(o2);
  return s ? i : i.concat(Xn(ts(o2)));
}
function lo(e) {
  return Object.assign({}, e, {
    left: e.x,
    top: e.y,
    right: e.x + e.width,
    bottom: e.y + e.height
  });
}
function Jp(e, t) {
  var n = _n(e, false, t === "fixed");
  return n.top = n.top + e.clientTop, n.left = n.left + e.clientLeft, n.bottom = n.top + e.clientHeight, n.right = n.left + e.clientWidth, n.width = e.clientWidth, n.height = e.clientHeight, n.x = n.left, n.y = n.top, n;
}
function fi(e, t, n) {
  return t === _l ? lo(qp(e, n)) : an(t) ? Jp(t, n) : lo(Xp(Jt(e)));
}
function Qp(e) {
  var t = Xn(ts(e)), n = ["absolute", "fixed"].indexOf(Ht(e).position) >= 0, a = n && Dt(e) ? ua(e) : e;
  return an(a) ? t.filter(function(s) {
    return an(s) && Ol(s, a) && jt(s) !== "body";
  }) : [];
}
function em(e, t, n, a) {
  var s = t === "clippingParents" ? Qp(e) : [].concat(t), r = [].concat(s, [n]), o2 = r[0], i = r.reduce(function(l, c) {
    var u = fi(e, c, a);
    return l.top = tn(u.top, l.top), l.right = xa(u.right, l.right), l.bottom = xa(u.bottom, l.bottom), l.left = tn(u.left, l.left), l;
  }, fi(e, o2, a));
  return i.width = i.right - i.left, i.height = i.bottom - i.top, i.x = i.left, i.y = i.top, i;
}
function Ml(e) {
  var t = e.reference, n = e.element, a = e.placement, s = a ? Bt(a) : null, r = a ? En(a) : null, o2 = t.x + t.width / 2 - n.width / 2, i = t.y + t.height / 2 - n.height / 2, l;
  switch (s) {
    case pt:
      l = {
        x: o2,
        y: t.y - n.height
      };
      break;
    case St:
      l = {
        x: o2,
        y: t.y + t.height
      };
      break;
    case Ct:
      l = {
        x: t.x + t.width,
        y: i
      };
      break;
    case mt:
      l = {
        x: t.x - n.width,
        y: i
      };
      break;
    default:
      l = {
        x: t.x,
        y: t.y
      };
  }
  var c = s ? Lo(s) : null;
  if (c != null) {
    var u = c === "y" ? "height" : "width";
    switch (r) {
      case Cn:
        l[c] = l[c] - (t[u] / 2 - n[u] / 2);
        break;
      case aa:
        l[c] = l[c] + (t[u] / 2 - n[u] / 2);
        break;
    }
  }
  return l;
}
function sa(e, t) {
  t === void 0 && (t = {});
  var n = t, a = n.placement, s = a === void 0 ? e.placement : a, r = n.strategy, o2 = r === void 0 ? e.strategy : r, i = n.boundary, l = i === void 0 ? $p : i, c = n.rootBoundary, u = c === void 0 ? _l : c, h = n.elementContext, p = h === void 0 ? Vn : h, v = n.altBoundary, w = v === void 0 ? false : v, $ = n.padding, b = $ === void 0 ? 0 : $, m = Al(typeof b != "number" ? b : Pl(b, ca)), y = p === Vn ? Dp : Vn, S = e.rects.popper, d = e.elements[w ? y : p], f = em(an(d) ? d : d.contextElement || Jt(e.elements.popper), l, u, o2), g = _n(e.elements.reference), k = Ml({
    reference: g,
    element: S,
    strategy: "absolute",
    placement: s
  }), M = lo(Object.assign({}, S, k)), A = p === Vn ? M : g, I = {
    top: f.top - A.top + m.top,
    bottom: A.bottom - f.bottom + m.bottom,
    left: f.left - A.left + m.left,
    right: A.right - f.right + m.right
  }, oe = e.modifiersData.offset;
  if (p === Vn && oe) {
    var ce = oe[s];
    Object.keys(I).forEach(function(R) {
      var N = [Ct, St].indexOf(R) >= 0 ? 1 : -1, B = [pt, St].indexOf(R) >= 0 ? "y" : "x";
      I[R] += ce[B] * N;
    });
  }
  return I;
}
function tm(e, t) {
  t === void 0 && (t = {});
  var n = t, a = n.placement, s = n.boundary, r = n.rootBoundary, o2 = n.padding, i = n.flipVariations, l = n.allowedAutoPlacements, c = l === void 0 ? El : l, u = En(a), h = u ? i ? li : li.filter(function(w) {
    return En(w) === u;
  }) : ca, p = h.filter(function(w) {
    return c.indexOf(w) >= 0;
  });
  p.length === 0 && (p = h);
  var v = p.reduce(function(w, $) {
    return w[$] = sa(e, {
      placement: $,
      boundary: s,
      rootBoundary: r,
      padding: o2
    })[Bt($)], w;
  }, {});
  return Object.keys(v).sort(function(w, $) {
    return v[w] - v[$];
  });
}
function nm(e) {
  if (Bt(e) === To) return [];
  var t = Aa(e);
  return [di(e), t, di(t)];
}
function am(e) {
  var t = e.state, n = e.options, a = e.name;
  if (!t.modifiersData[a]._skip) {
    for (var s = n.mainAxis, r = s === void 0 ? true : s, o2 = n.altAxis, i = o2 === void 0 ? true : o2, l = n.fallbackPlacements, c = n.padding, u = n.boundary, h = n.rootBoundary, p = n.altBoundary, v = n.flipVariations, w = v === void 0 ? true : v, $ = n.allowedAutoPlacements, b = t.options.placement, m = Bt(b), y = m === b, S = l || (y || !w ? [Aa(b)] : nm(b)), d = [b].concat(S).reduce(function(x, U) {
      return x.concat(Bt(U) === To ? tm(t, {
        placement: U,
        boundary: u,
        rootBoundary: h,
        padding: c,
        flipVariations: w,
        allowedAutoPlacements: $
      }) : U);
    }, []), f = t.rects.reference, g = t.rects.popper, k = /* @__PURE__ */ new Map(), M = true, A = d[0], I = 0; I < d.length; I++) {
      var oe = d[I], ce = Bt(oe), R = En(oe) === Cn, N = [pt, St].indexOf(ce) >= 0, B = N ? "width" : "height", G = sa(t, {
        placement: oe,
        boundary: u,
        rootBoundary: h,
        altBoundary: p,
        padding: c
      }), j = N ? R ? Ct : mt : R ? St : pt;
      f[B] > g[B] && (j = Aa(j));
      var J = Aa(j), q = [];
      if (r && q.push(G[ce] <= 0), i && q.push(G[j] <= 0, G[J] <= 0), q.every(function(x) {
        return x;
      })) {
        A = oe, M = false;
        break;
      }
      k.set(oe, q);
    }
    if (M) for (var fe = w ? 3 : 1, we = function(U) {
      var le = d.find(function(_e) {
        var ve = k.get(_e);
        if (ve) return ve.slice(0, U).every(function(he) {
          return he;
        });
      });
      if (le) return A = le, "break";
    }, ge = fe; ge > 0; ge--) {
      var Te = we(ge);
      if (Te === "break") break;
    }
    t.placement !== A && (t.modifiersData[a]._skip = true, t.placement = A, t.reset = true);
  }
}
var sm = {
  name: "flip",
  enabled: true,
  phase: "main",
  fn: am,
  requiresIfExists: ["offset"],
  data: {
    _skip: false
  }
};
function hi(e, t, n) {
  return n === void 0 && (n = {
    x: 0,
    y: 0
  }), {
    top: e.top - t.height - n.y,
    right: e.right - t.width + n.x,
    bottom: e.bottom - t.height + n.y,
    left: e.left - t.width - n.x
  };
}
function pi(e) {
  return [pt, Ct, St, mt].some(function(t) {
    return e[t] >= 0;
  });
}
function om(e) {
  var t = e.state, n = e.name, a = t.rects.reference, s = t.rects.popper, r = t.modifiersData.preventOverflow, o2 = sa(t, {
    elementContext: "reference"
  }), i = sa(t, {
    altBoundary: true
  }), l = hi(o2, a), c = hi(i, s, r), u = pi(l), h = pi(c);
  t.modifiersData[n] = {
    referenceClippingOffsets: l,
    popperEscapeOffsets: c,
    isReferenceHidden: u,
    hasPopperEscaped: h
  }, t.attributes.popper = Object.assign({}, t.attributes.popper, {
    "data-popper-reference-hidden": u,
    "data-popper-escaped": h
  });
}
var rm = {
  name: "hide",
  enabled: true,
  phase: "main",
  requiresIfExists: ["preventOverflow"],
  fn: om
};
function im(e, t, n) {
  var a = Bt(e), s = [mt, pt].indexOf(a) >= 0 ? -1 : 1, r = typeof n == "function" ? n(Object.assign({}, t, {
    placement: e
  })) : n, o2 = r[0], i = r[1];
  return o2 = o2 || 0, i = (i || 0) * s, [mt, Ct].indexOf(a) >= 0 ? {
    x: i,
    y: o2
  } : {
    x: o2,
    y: i
  };
}
function lm(e) {
  var t = e.state, n = e.options, a = e.name, s = n.offset, r = s === void 0 ? [0, 0] : s, o2 = El.reduce(function(u, h) {
    return u[h] = im(h, t.rects, r), u;
  }, {}), i = o2[t.placement], l = i.x, c = i.y;
  t.modifiersData.popperOffsets != null && (t.modifiersData.popperOffsets.x += l, t.modifiersData.popperOffsets.y += c), t.modifiersData[a] = o2;
}
var cm = {
  name: "offset",
  enabled: true,
  phase: "main",
  requires: ["popperOffsets"],
  fn: lm
};
function um(e) {
  var t = e.state, n = e.name;
  t.modifiersData[n] = Ml({
    reference: t.rects.reference,
    element: t.rects.popper,
    strategy: "absolute",
    placement: t.placement
  });
}
var dm = {
  name: "popperOffsets",
  enabled: true,
  phase: "read",
  fn: um,
  data: {}
};
function fm(e) {
  return e === "x" ? "y" : "x";
}
function hm(e) {
  var t = e.state, n = e.options, a = e.name, s = n.mainAxis, r = s === void 0 ? true : s, o2 = n.altAxis, i = o2 === void 0 ? false : o2, l = n.boundary, c = n.rootBoundary, u = n.altBoundary, h = n.padding, p = n.tether, v = p === void 0 ? true : p, w = n.tetherOffset, $ = w === void 0 ? 0 : w, b = sa(t, {
    boundary: l,
    rootBoundary: c,
    padding: h,
    altBoundary: u
  }), m = Bt(t.placement), y = En(t.placement), S = !y, d = Lo(m), f = fm(d), g = t.modifiersData.popperOffsets, k = t.rects.reference, M = t.rects.popper, A = typeof $ == "function" ? $(Object.assign({}, t.rects, {
    placement: t.placement
  })) : $, I = typeof A == "number" ? {
    mainAxis: A,
    altAxis: A
  } : Object.assign({
    mainAxis: 0,
    altAxis: 0
  }, A), oe = t.modifiersData.offset ? t.modifiersData.offset[t.placement] : null, ce = {
    x: 0,
    y: 0
  };
  if (g) {
    if (r) {
      var R, N = d === "y" ? pt : mt, B = d === "y" ? St : Ct, G = d === "y" ? "height" : "width", j = g[d], J = j + b[N], q = j - b[B], fe = v ? -M[G] / 2 : 0, we = y === Cn ? k[G] : M[G], ge = y === Cn ? -M[G] : -k[G], Te = t.elements.arrow, x = v && Te ? Eo(Te) : {
        width: 0,
        height: 0
      }, U = t.modifiersData["arrow#persistent"] ? t.modifiersData["arrow#persistent"].padding : Il(), le = U[N], _e = U[B], ve = qn(0, k[G], x[G]), he = S ? k[G] / 2 - fe - ve - le - I.mainAxis : we - ve - le - I.mainAxis, Pe = S ? -k[G] / 2 + fe + ve + _e + I.mainAxis : ge + ve + _e + I.mainAxis, Ve = t.elements.arrow && ua(t.elements.arrow), gt = Ve ? d === "y" ? Ve.clientTop || 0 : Ve.clientLeft || 0 : 0, D = (R = oe == null ? void 0 : oe[d]) != null ? R : 0, T = j + he - D - gt, F = j + Pe - D, W = qn(v ? xa(J, T) : J, j, v ? tn(q, F) : q);
      g[d] = W, ce[d] = W - j;
    }
    if (i) {
      var re, be = d === "x" ? pt : mt, ot = d === "x" ? St : Ct, Fe = g[f], X = f === "y" ? "height" : "width", _ = Fe + b[be], P = Fe - b[ot], te = [pt, mt].indexOf(m) !== -1, ye = (re = oe == null ? void 0 : oe[f]) != null ? re : 0, Ke = te ? _ : Fe - k[X] - M[X] - ye + I.altAxis, ct = te ? Fe + k[X] + M[X] - ye - I.altAxis : P, vt = v && te ? Fp(Ke, Fe, ct) : qn(v ? Ke : _, Fe, v ? ct : P);
      g[f] = vt, ce[f] = vt - Fe;
    }
    t.modifiersData[a] = ce;
  }
}
var pm = {
  name: "preventOverflow",
  enabled: true,
  phase: "main",
  fn: hm,
  requiresIfExists: ["offset"]
};
function mm(e) {
  return {
    scrollLeft: e.scrollLeft,
    scrollTop: e.scrollTop
  };
}
function gm(e) {
  return e === Et(e) || !Dt(e) ? Oo(e) : mm(e);
}
function vm(e) {
  var t = e.getBoundingClientRect(), n = Tn(t.width) / e.offsetWidth || 1, a = Tn(t.height) / e.offsetHeight || 1;
  return n !== 1 || a !== 1;
}
function bm(e, t, n) {
  n === void 0 && (n = false);
  var a = Dt(t), s = Dt(t) && vm(t), r = Jt(t), o2 = _n(e, s, n), i = {
    scrollLeft: 0,
    scrollTop: 0
  }, l = {
    x: 0,
    y: 0
  };
  return (a || !a && !n) && ((jt(t) !== "body" || Ao(r)) && (i = gm(t)), Dt(t) ? (l = _n(t, true), l.x += t.clientLeft, l.y += t.clientTop) : r && (l.x = Io(r))), {
    x: o2.left + i.scrollLeft - l.x,
    y: o2.top + i.scrollTop - l.y,
    width: o2.width,
    height: o2.height
  };
}
function ym(e) {
  var t = /* @__PURE__ */ new Map(), n = /* @__PURE__ */ new Set(), a = [];
  e.forEach(function(r) {
    t.set(r.name, r);
  });
  function s(r) {
    n.add(r.name);
    var o2 = [].concat(r.requires || [], r.requiresIfExists || []);
    o2.forEach(function(i) {
      if (!n.has(i)) {
        var l = t.get(i);
        l && s(l);
      }
    }), a.push(r);
  }
  return e.forEach(function(r) {
    n.has(r.name) || s(r);
  }), a;
}
function $m(e) {
  var t = ym(e);
  return Ip.reduce(function(n, a) {
    return n.concat(t.filter(function(s) {
      return s.phase === a;
    }));
  }, []);
}
function Dm(e) {
  var t;
  return function() {
    return t || (t = new Promise(function(n) {
      Promise.resolve().then(function() {
        t = void 0, n(e());
      });
    })), t;
  };
}
function wm(e) {
  var t = e.reduce(function(n, a) {
    var s = n[a.name];
    return n[a.name] = s ? Object.assign({}, s, a, {
      options: Object.assign({}, s.options, a.options),
      data: Object.assign({}, s.data, a.data)
    }) : a, n;
  }, {});
  return Object.keys(t).map(function(n) {
    return t[n];
  });
}
var mi = {
  placement: "bottom",
  modifiers: [],
  strategy: "absolute"
};
function gi() {
  for (var e = arguments.length, t = new Array(e), n = 0; n < e; n++) t[n] = arguments[n];
  return !t.some(function(a) {
    return !(a && typeof a.getBoundingClientRect == "function");
  });
}
function km(e) {
  e === void 0 && (e = {});
  var t = e, n = t.defaultModifiers, a = n === void 0 ? [] : n, s = t.defaultOptions, r = s === void 0 ? mi : s;
  return function(i, l, c) {
    c === void 0 && (c = r);
    var u = {
      placement: "bottom",
      orderedModifiers: [],
      options: Object.assign({}, mi, r),
      modifiersData: {},
      elements: {
        reference: i,
        popper: l
      },
      attributes: {},
      styles: {}
    }, h = [], p = false, v = {
      state: u,
      setOptions: function(m) {
        var y = typeof m == "function" ? m(u.options) : m;
        $(), u.options = Object.assign({}, r, u.options, y), u.scrollParents = {
          reference: an(i) ? Xn(i) : i.contextElement ? Xn(i.contextElement) : [],
          popper: Xn(l)
        };
        var S = $m(wm([].concat(a, u.options.modifiers)));
        return u.orderedModifiers = S.filter(function(d) {
          return d.enabled;
        }), w(), v.update();
      },
      forceUpdate: function() {
        if (!p) {
          var m = u.elements, y = m.reference, S = m.popper;
          if (gi(y, S)) {
            u.rects = {
              reference: bm(y, ua(S), u.options.strategy === "fixed"),
              popper: Eo(S)
            }, u.reset = false, u.placement = u.options.placement, u.orderedModifiers.forEach(function(I) {
              return u.modifiersData[I.name] = Object.assign({}, I.data);
            });
            for (var d = 0; d < u.orderedModifiers.length; d++) {
              if (u.reset === true) {
                u.reset = false, d = -1;
                continue;
              }
              var f = u.orderedModifiers[d], g = f.fn, k = f.options, M = k === void 0 ? {} : k, A = f.name;
              typeof g == "function" && (u = g({
                state: u,
                options: M,
                name: A,
                instance: v
              }) || u);
            }
          }
        }
      },
      update: Dm(function() {
        return new Promise(function(b) {
          v.forceUpdate(), b(u);
        });
      }),
      destroy: function() {
        $(), p = true;
      }
    };
    if (!gi(i, l)) return v;
    v.setOptions(c).then(function(b) {
      !p && c.onFirstUpdate && c.onFirstUpdate(b);
    });
    function w() {
      u.orderedModifiers.forEach(function(b) {
        var m = b.name, y = b.options, S = y === void 0 ? {} : y, d = b.effect;
        if (typeof d == "function") {
          var f = d({
            state: u,
            name: m,
            instance: v,
            options: S
          }), g = function() {
          };
          h.push(f || g);
        }
      });
    }
    function $() {
      h.forEach(function(b) {
        return b();
      }), h = [];
    }
    return v;
  };
}
var Sm = [Yp, dm, zp, Np, cm, sm, pm, Vp, rm];
var ns = km({
  defaultModifiers: Sm
});
var Po = {};
var No = {};
var as = {};
Object.defineProperty(as, "__esModule", {
  value: true
});
var xm = function(e) {
  if ("getBBox" in e) {
    var t = e.getBBox();
    return Object.freeze({
      height: t.height,
      left: 0,
      top: 0,
      width: t.width
    });
  } else {
    var n = window.getComputedStyle(e);
    return Object.freeze({
      height: parseFloat(n.height || "0"),
      left: parseFloat(n.paddingLeft || "0"),
      top: parseFloat(n.paddingTop || "0"),
      width: parseFloat(n.width || "0")
    });
  }
};
as.ContentRect = xm;
Object.defineProperty(No, "__esModule", {
  value: true
});
var jm = as;
var Vm = function() {
  function e(t) {
    this.target = t, this.$$broadcastWidth = this.$$broadcastHeight = 0;
  }
  return Object.defineProperty(e.prototype, "broadcastWidth", {
    get: function() {
      return this.$$broadcastWidth;
    },
    enumerable: true,
    configurable: true
  }), Object.defineProperty(e.prototype, "broadcastHeight", {
    get: function() {
      return this.$$broadcastHeight;
    },
    enumerable: true,
    configurable: true
  }), e.prototype.isActive = function() {
    var t = jm.ContentRect(this.target);
    return !!t && (t.width !== this.broadcastWidth || t.height !== this.broadcastHeight);
  }, e;
}();
No.ResizeObservation = Vm;
var Mo = {};
Object.defineProperty(Mo, "__esModule", {
  value: true
});
var Um = as;
var Wm = /* @__PURE__ */ function() {
  function e(t) {
    this.target = t, this.contentRect = Um.ContentRect(t);
  }
  return e;
}();
Mo.ResizeObserverEntry = Wm;
Object.defineProperty(Po, "__esModule", {
  value: true
});
var Hm = No;
var zm = Mo;
var zt = [];
var Fl = function() {
  function e(t) {
    this.$$observationTargets = [], this.$$activeTargets = [], this.$$skippedTargets = [];
    var n = Ym(t);
    if (n) throw TypeError(n);
    this.$$callback = t;
  }
  return e.prototype.observe = function(t) {
    var n = bi("observe", t);
    if (n) throw TypeError(n);
    var a = yi(this.$$observationTargets, t);
    a >= 0 || (this.$$observationTargets.push(new Hm.ResizeObservation(t)), Gm(this));
  }, e.prototype.unobserve = function(t) {
    var n = bi("unobserve", t);
    if (n) throw TypeError(n);
    var a = yi(this.$$observationTargets, t);
    a < 0 || (this.$$observationTargets.splice(a, 1), this.$$observationTargets.length === 0 && vi(this));
  }, e.prototype.disconnect = function() {
    this.$$observationTargets = [], this.$$activeTargets = [], vi(this);
  }, e;
}();
Po.ResizeObserver = Fl;
function Gm(e) {
  var t = zt.indexOf(e);
  t < 0 && (zt.push(e), Qm());
}
function vi(e) {
  var t = zt.indexOf(e);
  t >= 0 && (zt.splice(t, 1), e0());
}
function Ym(e) {
  if (typeof e > "u") return "Failed to construct 'ResizeObserver': 1 argument required, but only 0 present.";
  if (typeof e != "function") return "Failed to construct 'ResizeObserver': The callback provided as parameter 1 is not a function.";
}
function bi(e, t) {
  if (typeof t > "u") return "Failed to execute '" + e + "' on 'ResizeObserver': 1 argument required, but only 0 present.";
  if (!(t && t.nodeType === window.Node.ELEMENT_NODE)) return "Failed to execute '" + e + "' on 'ResizeObserver': parameter 1 is not of type 'Element'.";
}
function yi(e, t) {
  for (var n = 0; n < e.length; n += 1) if (e[n].target === t) return n;
  return -1;
}
var $i = function(e) {
  zt.forEach(function(t) {
    t.$$activeTargets = [], t.$$skippedTargets = [], t.$$observationTargets.forEach(function(n) {
      if (n.isActive()) {
        var a = Bl(n.target);
        a > e ? t.$$activeTargets.push(n) : t.$$skippedTargets.push(n);
      }
    });
  });
};
var Zm = function() {
  return zt.some(function(e) {
    return !!e.$$activeTargets.length;
  });
};
var Km = function() {
  return zt.some(function(e) {
    return !!e.$$skippedTargets.length;
  });
};
var qm = function() {
  var e = 1 / 0;
  return zt.forEach(function(t) {
    if (t.$$activeTargets.length) {
      var n = [];
      t.$$activeTargets.forEach(function(a) {
        var s = new zm.ResizeObserverEntry(a.target);
        n.push(s), a.$$broadcastWidth = s.contentRect.width, a.$$broadcastHeight = s.contentRect.height;
        var r = Bl(a.target);
        r < e && (e = r);
      }), t.$$callback(n, t), t.$$activeTargets = [];
    }
  }), e;
};
var Xm = function() {
  var e = new window.ErrorEvent("ResizeLoopError", {
    message: "ResizeObserver loop completed with undelivered notifications."
  });
  window.dispatchEvent(e);
};
var Bl = function(e) {
  for (var t = 0; e.parentNode; ) e = e.parentNode, t += 1;
  return t;
};
var Jm = function() {
  var e = 0;
  for ($i(e); Zm(); ) e = qm(), $i(e);
  Km() && Xm();
};
var Jn;
var Qm = function() {
  Jn || xl();
};
var xl = function() {
  Jn = window.requestAnimationFrame(function() {
    Jm(), xl();
  });
};
var e0 = function() {
  Jn && !zt.some(function(e) {
    return !!e.$$observationTargets.length;
  }) && (window.cancelAnimationFrame(Jn), Jn = void 0);
};
var t0 = function() {
  return window.ResizeObserver = Fl;
};
Po.install = t0;
var n0 = typeof global == "object" && global && global.Object === Object && global;
var a0 = n0;
var s0 = typeof self == "object" && self && self.Object === Object && self;
var o0 = a0 || s0 || Function("return this")();
var jl = o0;
var r0 = jl.Symbol;
var ja = r0;
var Vl = Object.prototype;
var i0 = Vl.hasOwnProperty;
var l0 = Vl.toString;
var Un = ja ? ja.toStringTag : void 0;
var u0 = Object.prototype;
var d0 = u0.toString;
var Di = ja ? ja.toStringTag : void 0;
var Ro = {
  theme: {
    type: String,
    default: ""
  },
  checked: {
    type: Boolean,
    default: false
  },
  label: {
    type: String,
    default: ""
  },
  value: {
    type: [String, Number, Boolean, void 0, null],
    default: ""
  },
  disabled: {
    type: Boolean,
    default: false
  },
  shape: {
    type: String,
    default: "square"
  }
};
var m2 = {
  inputType: {
    type: String,
    default: "checkbox"
  },
  ...ia(Ro, [])
};
var g2 = {
  ...ia(Ro, [])
};
var v2 = {
  shape: {
    type: String,
    default: "round"
  },
  ...ia(Ro, ["shape"])
};
var b2 = {
  theme: {
    type: String,
    default: ""
  },
  modelValue: {
    type: Array,
    default: () => []
  },
  options: {
    type: Array,
    default: () => []
  },
  gap: {
    type: Number,
    default: 20
  },
  disabled: {
    type: Boolean,
    default: false
  }
};
var y2 = {
  ...ia(b2, ["modelValue"]),
  modelValue: {
    type: [String, Number, Boolean],
    default: () => ""
  }
};
var Dn = ((e) => (e.Dialog = "dialog", e.Confirm = "confirm", e))(Dn || {});
var Fo = ((e) => (e.Small = "small", e.Normal = "normal", e.Large = "large", e))(Fo || {});
var da = ((e) => (e.Success = "success", e.Warning = "warning", e.Error = "error", e.Info = "info", e))(da || {});
var An = ((e) => (e.Left = "left", e.Center = "center", e.Right = "right", e))(An || {});
var Gl = ((e) => (e.Row = "row", e.Column = "column", e))(Gl || {});
var Yl = {
  theme: {
    type: String,
    default: Ie.Light
  },
  showConfirm: {
    type: Boolean,
    default: true
  },
  footerFlex: {
    type: String,
    default: "row"
  },
  confirmText: {
    type: String,
    default: ""
  },
  confirmProps: {
    type: Object,
    default: () => ({})
  },
  showCancel: {
    type: Boolean,
    default: true
  },
  cancelText: {
    type: String,
    default: ""
  },
  cancelProps: {
    type: Object,
    default: () => ({})
  }
};
var Zl = {
  dialogType: {
    type: String,
    default: "dialog"
  },
  theme: {
    type: String,
    default: ""
  },
  visible: {
    type: [Boolean, Object],
    default: false
  },
  title: {
    type: String,
    default: ""
  },
  message: {
    type: String,
    default: ""
  },
  width: {
    type: [String, Number],
    default: ""
  },
  isMaxWidth: {
    type: Boolean,
    default: false
  },
  size: {
    type: String,
    default: "normal"
  },
  minHeight: {
    type: [String, Number],
    default: 174
  },
  maxHeight: {
    type: [String, Number],
    default: 700
  },
  icon: {
    type: String,
    default: ""
  },
  align: {
    type: String,
    default: ""
  },
  showFooter: {
    type: Boolean,
    default: true
  },
  showClose: {
    type: Boolean,
    default: true
  },
  closeSize: {
    type: [String, Number],
    default: 16
  },
  zIndex: {
    type: Number,
    default: 1001
  },
  lockBodyScroll: {
    type: Boolean,
    default: true
  },
  mask: {
    type: Boolean,
    default: true
  },
  maskClosable: {
    type: Boolean,
    default: true
  },
  routerClose: {
    type: Boolean,
    default: true
  },
  appendToBody: {
    type: Boolean,
    default: false
  },
  placement: {
    type: String,
    default: ""
  },
  jsDestroy: {
    type: Function,
    default: null
  },
  dialogDestroy: {
    type: Function,
    default: null
  },
  ...ia(Yl, ["theme"])
};
({
  ...Zl
});
var k4 = {
  theme: {
    type: String,
    default: Ie.Light
  },
  icon: {
    type: String,
    default: ""
  },
  title: {
    type: String,
    default: ""
  },
  message: {
    type: String,
    default: ""
  }
};
var S4 = {
  theme: {
    type: String,
    default: Ie.Light
  },
  icon: {
    type: String,
    default: ""
  }
};
var By = {
  dialogType: Dn.Confirm,
  mask: false,
  size: Fo.Small,
  align: An.Left,
  lockBodyScroll: false,
  showClose: false,
  minHeight: "auto"
};
var Na = ((e) => (e.DATE = "date", e.RANGE = "daterange", e.TIME = "time", e.DATETIME = "datetime", e.RANGETIME = "datetimerange", e))(Na || {});
var YS = Date.now();
var ZS = 2e3;
var Ri = 0;
function ec() {
  const e = Ri;
  return Ri += 1, `message_${YS}_${e}`;
}
function KS(e) {
  return Object.prototype.toString.call(e) === "[object Object]" && !!e.content;
}
var wn = class _wn {
  constructor() {
    this.messages = [];
  }
  static getInstance() {
    return _wn.instance || (_wn.instance = new _wn()), _wn.instance;
  }
  add(t) {
    if (this.messages.push(t), this.div && (this.vm || this.instance)) {
      this.vm.component.proxy.add && this.vm.component.proxy.add(t);
      return;
    }
    this.render(t);
  }
  destroy(t) {
    const {
      uuid: n
    } = t, a = this.messages.findIndex((s) => s.uuid === n);
    this.messages.splice(a, 1), this.messages.length || setTimeout(() => {
      this.messages.length || (Ft && Ft(null, this.div), this.div.parentNode && this.div.parentNode.removeChild(this.div), this.div = null, this.vm = null);
    }, 300);
  }
  render(t) {
    this.div = document.createElement("div"), document.body.appendChild(this.div), this.vm = $e(GS), Ft(this.vm, this.div), this.vm.component.proxy.setCallback && this.vm.component.proxy.setCallback({
      destroy: this.destroy.bind(this)
    }), this.vm.component.proxy.add && this.vm.component.proxy.add(t);
  }
};
var qS = class {
  open(t) {
    if (Sn()) return;
    const n = wn.getInstance(), a = {
      duration: t.duration || ZS,
      ...t
    };
    a.uuid || (a.uuid = ec()), n.add(a);
  }
};
var tc = new qS();
var XS = (e, t) => {
  e[t] = (n, a) => {
    const s = ec();
    return KS(n) ? e.open({
      ...n,
      uuid: s,
      type: t
    }) : e.open({
      uuid: s,
      content: n,
      type: t,
      onClose: a,
      closable: !!a
    });
  };
};
["info", "error", "success", "warn"].forEach((e) => XS(tc, e));
