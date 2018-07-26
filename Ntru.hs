module Ntru where

import Prelude hiding ((!!), take, drop, replicate, length, mod)

import Crypto.Random.DRBG

import Control.Monad.CryptoRandom (crandomR)
import Control.Monad.Fix (fix)

import Data.List (transpose)
import Data.Maybe (isNothing, fromJust)

import Debug.Trace

import Polynomial hiding (main)


type RandomGenerator = GenAutoReseed CtrDRBG SystemRandom

newtype Keypair t = Keypair (Polynomial t, Polynomial t)

instance (Integral a, Show a) => Show (Keypair a) where
    show (Keypair (pub, priv)) = "public: " ++ show pub ++ " private: " ++ show priv

newtype Params t = Params (Integer, Integer, t, (t, Integer))

instance (Integral a, Show a) => Show (Params a) where
    show (Params (n, d, p, (q, m))) = foldl1 (++) (concat $ transpose [["N=", " d=", " p=", " q="], [show n, show d, show p, show (q ^ m)]])


setAt :: (Integral t) => [t] -> Integer -> t -> [t]
setAt xs i x = take i xs ++ [x] ++ drop (i + 1) xs


randomPoly :: (Integral t) => RandomGenerator -> Params t -> IO (RandomGenerator, Polynomial t)
randomPoly gen (Params (n, d, _, _)) = do
    let zero = replicate n 0
    let randomPolyDelta = \loop (xs, gen, delta, n) -> do
        if n /= 0 then
            let (r, gen') = throwLeft $ crandomR (0, length xs - 1) gen in
            if (xs !! r) == 0 then
                loop (setAt xs r delta, gen', delta, n-1)
            else
                loop (xs, gen', delta, n)
        else
            return (xs, gen)
    (xs, gen) <- flip fix (zero, gen, 1, d) randomPolyDelta
    (ys, gen) <- flip fix (xs, gen, -1, d-1) randomPolyDelta
    return $ (gen, Polynomial ys)

keygen :: (Integral t) => RandomGenerator -> Params t -> IO (RandomGenerator, Keypair t)
keygen gen params = do
    (gen, f, fq) <- flip fix gen $ \loop gen -> do
        (gen, r)  <- randomPoly gen params
        let f = (r `mul` Polynomial [p]) `add` Polynomial [1]
        let fq = f `inverseModPn` qr
        if isNothing fq then
            loop gen
        else
            return (gen, f, fromJust fq)
    (gen, g) <- randomPoly gen params
    let h = (fq `mul` g `mul` Polynomial [p]) `mod` (q ^ r)
    return $ (gen, Keypair (h, f))
  where (Params (_, _, p, qr)) = params
        (q, r) = qr


main :: IO ()
main = do
    let params = Params (251, 8, 3, (3, 8))
    gen <- newGenAutoReseedIO (2^32) :: IO RandomGenerator
    (gen, key) <- keygen gen params
    print key
