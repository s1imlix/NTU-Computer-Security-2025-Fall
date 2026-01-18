const fs = require('fs');
const path = './_next/static/chunks/app/page-a5d5f48bdef4decb.js';

try {
    const content = fs.readFileSync(path, 'utf8');

    // Helper to extract code block
    function extractFunction(source, startStr, endStr) {
        const start = source.indexOf(startStr);
        if (start === -1) return null;
        const end = source.indexOf(endStr, start);
        if (end === -1) return null;
        return source.substring(start, end + endStr.length);
    }

    // 1. Extract p() - The string array
    const pCode = extractFunction(content, 'function p(){', 'return(p=function(){return t})()}');

    // 2. Extract I() - The lookup function
    const iCode = extractFunction(content, 'function I(t,e){', 'return t-=336,p()[t]}');

    // 3. Extract Rotation IIFE
    // The IIFE structure is !function(t,e){let i=I,s=t();...}(p,0);
    const rotStartStr = '!function(t,e){let i=I,s=t();';
    const rotEndStr = '}(p,0);';
    const rotCode = extractFunction(content, rotStartStr, rotEndStr);

    if (!pCode || !iCode || !rotCode) {
        console.error("Failed to extract code parts");
        console.log("pCode found:", !!pCode);
        console.log("iCode found:", !!iCode);
        console.log("rotCode found:", !!rotCode);
        process.exit(1);
    }

    // Assemble and run
    const evalCode = `
        ${pCode}
        ${iCode}
        const T = I;
        ${rotCode}
        
        // The B variable logic from the file:
        // let B=(null!=(N=T(1267)+T(1399)+T(1138)+T(469)+T(611))?N:T(1267)+T(1399)+"c.cha"+T(469)+T(611)).replace(/\/$/,"")
        
        const part1 = T(1267);
        const part2 = T(1399);
        const part3 = T(1138);
        const part4 = T(469);
        const part5 = T(611);
        
        console.log("Part 1:", part1);
        console.log("Part 2:", part2);
        console.log("Part 3:", part3);
        console.log("Part 4:", part4);
        console.log("Part 5:", part5);
        
        const N = part1 + part2 + part3 + part4 + part5;
        console.log("Full URL:", N);
    `;

    eval(evalCode);

} catch (err) {
    console.error("Error:", err);
}