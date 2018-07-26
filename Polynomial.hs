module Polynomial where

import Prelude hiding (mod, exponent, length, (!!), replicate, take, drop)
import qualified Prelude

import Data.List (intercalate)
import Data.Maybe (isNothing, fromJust, fromMaybe)

import Debug.Trace


length :: [a] -> Integer
length = toInteger . Prelude.length

(!!) :: [a] -> Integer -> a
xs !! n = xs Prelude.!! fromInteger n

replicate :: Integer -> a -> [a]
replicate n = Prelude.replicate (fromInteger n)

take :: Integer -> [a] -> [a]
take n = Prelude.take (fromInteger n)

drop :: Integer -> [a] -> [a]
drop n = Prelude.drop (fromInteger n)


data Cond a = a :? a

infixl 0 ?
infixl 1 :?

(?) :: Bool -> Cond a -> a
True  ? (x :? _) = x
False ? (_ :? y) = y


denumerate :: (Integral b) => [a] -> b -> [(a,b)]
denumerate [] _ = []
denumerate (x:xs) n = (x,n):denumerate xs (n-1)

enumerate :: [a] -> [(a,Integer)]
enumerate [] = []
enumerate xs = reverse (denumerate (reverse xs) (length xs - 1))

ensureAtLeast :: (Num t) => [t] -> Integer -> [t]
ensureAtLeast xs n
  | length xs < n = ensureAtLeast (xs ++ [0]) n
  | otherwise = xs


newtype Polynomial t = Polynomial [t]

instance (Num a, Eq a, Show a) => Show (Polynomial a) where
    show (Polynomial xs) = show xs
    {-show (Polynomial xs) = intercalate " + " . filter (not . null) . map wrap $ enumerate xs
        where wrap (0, _) = ""
              wrap (1, 1) = "x"
              wrap (coefficient, 1) = show coefficient ++ "x"
              wrap (coefficient, 0) = show coefficient
              wrap (1, exponent) = "x^" ++ show exponent
              wrap (coefficient, exponent) = show coefficient ++ "x^" ++ show exponent-}


rshift :: Polynomial t -> Polynomial t
rshift (Polynomial xs) = Polynomial $ last xs:init xs

lshift :: Polynomial t -> Polynomial t
lshift (Polynomial xs) = Polynomial $ tail xs ++ [head xs]

lshiftn :: Polynomial t -> Integer -> Polynomial t
lshiftn p n
  | n > 0  = lshiftn (lshift p) (n - 1)
  | n == 0 = p
  | n < 0  = lshiftn (rshift p) (n + 1)


degree :: (Integral t) => Polynomial t -> Integer
degree (Polynomial xs)
  | all (== 0) xs    = 0
  | (xs !! ord) == 0 = degree (Polynomial $ init xs)
  | otherwise        = ord
    where ord = length xs - 1

centerlift :: (Integral t) => Polynomial t -> t -> Polynomial t
centerlift (Polynomial xs) n = Polynomial [c > n `quot` 2 ? c - n :? c | c <- xs]


add :: (Integral t) => Polynomial t -> Polynomial t -> Polynomial t
add (Polynomial xs) (Polynomial ys) = Polynomial $ zipWith (+) (ensureAtLeast xs maxRingSize) (ensureAtLeast ys maxRingSize)
    where maxRingSize = max (length xs) (length ys)

sub :: (Integral t) => Polynomial t -> Polynomial t -> Polynomial t
sub (Polynomial xs) (Polynomial ys) = Polynomial $ zipWith (-) (ensureAtLeast xs maxRingSize) (ensureAtLeast ys maxRingSize)
    where maxRingSize = max (length xs) (length ys)


modulo :: (Integral t) => t -> t -> t
modulo a b
  | a < 0     = modulo (a+b) b
  | otherwise = a `rem` b

mod :: (Integral t) => Polynomial t -> t -> Polynomial t
mod (Polynomial xs) n = Polynomial $ map (`modulo` n) xs

mul1 :: (Integral t) => Polynomial t -> Polynomial t -> Polynomial t
mul1 (Polynomial []) (Polynomial ys) = Polynomial $ replicate (length ys) 0
mul1 (Polynomial (x:xs)) (Polynomial ys) = add (Polynomial $ map (*x) ys) (rshift tail)
    where tail = mul1 (Polynomial xs) (Polynomial ys)

mul :: (Integral t) => Polynomial t -> Polynomial t -> Polynomial t
mul (Polynomial xs) (Polynomial ys) = mul1 (Polynomial $ ensureAtLeast xs maxRingSize) (Polynomial $ ensureAtLeast ys maxRingSize)
    where maxRingSize = max (length xs) (length ys)


swap :: [t] -> [t]
swap [a, b, c] = [a, c, b]

eea :: (Integral t) => t -> t -> [t]
eea a 0 = [a, 1, 0]
eea a b = let q = quot a b in
              let s = eea b (a - q * b) !! 2 in
                  swap (zipWith (-) (eea b (a - q * b)) [0, q * s, 0])

inv :: (Integral t) => t -> t -> Maybe t
inv a b
  | a == 0    = Nothing
  | a > 0     = (gcd == 1) ? Just (x `rem` b) :? Nothing
  | otherwise = inv ((a + b) `rem` b) b
    where [gcd, x, _] = eea a b


inverseStep :: (Integral t) => ([Polynomial t], t, Integer) -> Maybe ([Polynomial t], t, Integer)
inverseStep (ps, q, k)
 | isNothing nothingCriterion = Nothing
 | degree f == 0 = Just (ps, q, k)
 | head fs == 0  = Just ([lshift f, g, b, rshift c], q, succ k)
 | otherwise     = Just ([mod (sub f' (mul u g')) q, mod g' q, mod (sub b' (mul u c')) q, mod c' q], q, k)
   where [f, g, b, c] = ps
         nothingCriterion = inv (head gs) q
         g0Inv = fromJust nothingCriterion
         Polynomial fs    = f
         Polynomial gs    = g
         (f', g', b', c') = degree f < degree g ? (g, f, c, b) :? (f, g, b, c)
         u                = Polynomial [head fs * g0Inv]


inverseModP :: (Integral t, Show t) => Polynomial t -> t -> Maybe (Polynomial t)
inverseModP f p
  | isNothing nothingCriterion = Nothing
  | otherwise = Just $ mod (lshiftn (mul (Polynomial [h0Inv]) (Polynomial (init bs))) (k `rem` n)) p
    where n = length fs
          initial = (map Polynomial [fs ++ [0], -1:replicate (n - 1) 0 ++ [1], 1:replicate n 0, replicate (n + 1) 0], p, n)
          zero = (replicate 4 $ Polynomial [0], 0, 0)
          ([h, _, b, _], _, k) = until (\(ps, _, k) -> (degree (head ps) == 0) || (k > n * 3)) (fromMaybe zero . inverseStep) initial
          nothingCriterion = inv (head hs) p
          h0Inv = fromJust nothingCriterion
          Polynomial fs = f
          Polynomial hs = h
          Polynomial bs = b 


inverseModPn :: (Integral t, Show t) => Polynomial t -> (t, Integer) -> Maybe (Polynomial t)
inverseModPn f (p, r)
  | isNothing g = Nothing
  | otherwise   = Just $ mod h (p ^ r)
    where g = inverseModP f p
          initial = (fromJust g, toRational r, 2)
          (h, _, _) = until (\(_, x, _) -> x < 1) inverseStep initial
          inverseStep (g, r, n) = (g', r / 2, n * 2)
              where g' = mod (mul (sub (Polynomial [2]) (mul f g)) g) (p ^ n)


main :: IO()
main = do
    let f = Polynomial [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -3, -3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, -3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, -3, 0, -3, 0, 3, 0, 3, 0, 0, -3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, -3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0] :: Polynomial Integer
    let fp = fromJust $ f `inverseModP` 3
    let fq = fromJust $ f `inverseModPn` (3, 10)
    putStrLn $ foldl1 (++) ["invert f := ", show f, " mod 3 = \n f^-1 mod 3 := ", show fp]
    putStrLn $ foldl1 (++) ["f * f^-1 mod 3 = ", show $ (f `mul` fp) `mod` 3]
    putStrLn $ foldl1 (++) ["invert f := ", show f, ") mod 32 = \n f^-1 mod 32 := ", show fq]
    putStrLn $ foldl1 (++) ["f * f^-1 mod 32 = ", show $ (f `mul` fq) `mod` 32]
