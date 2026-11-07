# toonworld — cartoon street world for hybrid cut3d episodes

TypeScript source of `videos/<slug>/toonworld.js`. The look modules (toon, shade, cardshade, ink, lensblur, grade,
lights, paint) are adapted from the MIT-licensed claude-animated-shorts package; `world.ts` is the Thai street set
(shophouses, the clinic, a bubble-tea stall, power poles, a car, a bedroom corner) and the per-frame poser.

Build (three stays external, resolved by the engine's import map):

    npm i esbuild postprocessing@6.39.6
    npx esbuild tools/toonworld/world.ts --bundle --format=esm --external:three --outfile=videos/<slug>/toonworld.js

An episode imports it, creates `new ToonWorld(L.renderer, logo)` in setup(), and for a cartoon beat calls
`W.frame({...})`, then hides the cut3d scene for that frame (scene.visible=false, background=null, autoClear=false;
restore them in L.onReset).
