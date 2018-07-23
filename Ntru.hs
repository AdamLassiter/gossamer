module Ntru where

import Prelude hiding (mod, replicate, length, take, drop, (!!))
import Data.List (transpose)
import System.Random
import System.IO.Unsafe
import Polynomial hiding (main)


newtype Keypair t = Keypair (Polynomial t, Polynomial t)

instance (Num a, Eq a, Show a) => Show (Keypair a) where
    show (Keypair (pub, priv)) = "public: " ++ show pub ++ " private: " ++ show priv

newtype Params t = Params (Integer, Integer, Integer, t, t)

instance (Show a) => Show (Params a) where
    show (Params (n, d, hw, p, q)) = foldl1 (++) (concat $ transpose [["N=", " d=", " Hw=", " p=", " q="], [show n, show d, show hw, show p, show q]])


randPolyStep :: (Integral t) => (Polynomial t, (Integer, Integer)) -> (Polynomial t, (Integer, Integer))
randPolyStep (Polynomial xs, (pos, neg))
  | pos > 0   = (Polynomial $ next 1, (pos - (step ? 1 :? 0), neg))
  | neg > 0   = (Polynomial $ next (-1), (pos, neg - (step ? 1 :? 0)))
  | otherwise = (Polynomial xs, (0, 0))
    where next x = step ? take n xs ++ [x] ++ drop (n + 1) xs :? xs
          step = xs !! n == 0
          n = unsafePerformIO $ randomRIO (1, length xs)

randomPoly :: (Integral t) => Params t -> Polynomial t
randomPoly (Params (n, d, hw, _, _)) = p
    where p0 = Polynomial $ replicate n 0
          steps = listUntil (\(_, (i, j)) -> i == 0 && j == 0) randPolyStep (p0, (d, d-1))
          (p, _) = last steps


keygenStep :: (Integral t) => (Params t, Polynomial t) -> (Params t, Polynomial t)
keygenStep (params, _) = (params, randomPoly params `mul` Polynomial [p] `add` Polynomial [1])
    where (Params (_, _, _, p, _)) = params

keygen :: (Integral t) => Params t -> Keypair t
keygen params
  | isZero fq = keygen params
  | otherwise = Keypair (h, f)
    where (Params (_, _, _, p, q)) = params
          steps = listUntil (not . isZero . snd) keygenStep (params, Polynomial [0])
          (_, f)  = last steps
          fq = f `inverseModPn` q
          g  = randomPoly params
          h  = (fq `mul` g `mul` Polynomial [p]) `mod` p


main :: IO ()
main = let p = Polynomial [-1, 1, 1, 0, -1, 0, 1, 0, 0, 1, -1] in
       let params = Params (251, 8, 72, 3, 3^8) in 
           print $ keygen params
