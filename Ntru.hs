module Ntru where

import Prelude hiding ((!!), take, drop, replicate, length)

import Crypto.Random.DRBG

import Control.Monad.CryptoRandom (crandomR)
import Control.Monad.Fix (fix)

import Data.List (transpose)

import Polynomial hiding (main)


type RandomGenerator = GenAutoReseed CtrDRBG SystemRandom

newtype Keypair t = Keypair (Polynomial t, Polynomial t)

instance (Num a, Eq a, Show a) => Show (Keypair a) where
    show (Keypair (pub, priv)) = "public: " ++ show pub ++ " private: " ++ show priv

newtype Params t = Params (Integer, Integer, Integer, t, t)

instance (Show a) => Show (Params a) where
    show (Params (n, d, hw, p, q)) = foldl1 (++) (concat $ transpose [["N=", " d=", " Hw=", " p=", " q="], [show n, show d, show hw, show p, show q]])


setAt :: (Integral t) => [t] -> Integer -> t -> [t]
setAt xs i x = take i xs ++ [x] ++ drop (i + 1) xs

randomPoly :: (Integral t) => Params t -> IO (Polynomial t)
randomPoly (Params (n, d, _, _, _)) = do
    gen <- newGenAutoReseedIO (2^32) :: IO (GenAutoReseed CtrDRBG SystemRandom)
    let zero = replicate n 0
    let randomPolyDelta = (\loop (xs, gen, delta, n) -> do
        if n /= 0 then
                  let (r, gen') = throwLeft $ crandomR (0, length xs - 1) gen in
            if (xs !! r) == 0 then
                loop (setAt xs r delta, gen', delta, n-1)
            else
                loop (xs, gen', delta, n)
        else
            return (xs, gen))
    (xs, gen') <- flip fix (zero, gen, 1, d) randomPolyDelta
    (ys, gen'') <- flip fix (xs, gen', -1, d-1) randomPolyDelta
    return $ Polynomial ys


main :: IO ()
main = do
    r <- randomPoly (Params (13, 4, 0, 0, 0))
    print r
