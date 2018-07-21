import Prelude hiding (mod)
import Data.List (find, intercalate)
import Data.Maybe (fromMaybe)
import Debug.Trace (trace, traceShow)


data Cond a = a :? a

infixl 0 ?
infixl 1 :?

(?) :: Bool -> Cond a -> a
True  ? (x :? _) = x
False ? (_ :? y) = y


denumerate :: (Integral b) => [a] -> b -> [(a,b)]
denumerate [] _ = []
denumerate (x:xs) n = (x,n):denumerate xs (n-1)

enumerate :: [a] -> [(a,Int)]
enumerate [] = []
enumerate xs = reverse (denumerate (reverse xs) (length xs - 1))

ensureAtLeast :: (Num t) => [t] -> Int -> [t]
ensureAtLeast xs n
  | length xs < n = ensureAtLeast (0:xs) n
  | otherwise = xs


newtype Polynomial t = Polynomial [t]
newtype Keypair t = Keypair (t t)

instance (Num a, Eq a, Show a) => Show (Polynomial a) where
    show (Polynomial xs) = show xs
    --show (Polynomial xs) = intercalate " + " . filter (not . null) . map wrap $ enumerate xs
    --    where wrap (0, _) = ""
    --          wrap (1, 1) = "x"
    --          wrap (coefficient, 1) = show coefficient ++ "x"
    --          wrap (coefficient, 0) = show coefficient
    --          wrap (1, exponent) = "x^" ++ show exponent
    --          wrap (coefficient, exponent) = show coefficient ++ "x^" ++ show exponent


rshift :: Polynomial t -> Polynomial t
rshift (Polynomial xs) = Polynomial $ last xs:init xs

lshift :: Polynomial t -> Polynomial t
lshift (Polynomial xs) = Polynomial $ tail xs ++ [head xs]

lshiftn :: Polynomial t -> Int -> Polynomial t
lshiftn p n
  | n > 0  = lshiftn (lshift p) (n - 1)
  | n == 0 = p
  | n < 0  = lshiftn (rshift p) (n + 1)


degree :: (Num t, Eq t) => Polynomial t -> Int
degree (Polynomial xs)
  | all (== 0) xs    = 0
  | (xs !! ord) == 0 = degree (Polynomial $ init xs)
  | otherwise        = ord
    where ord = length xs - 1

centerlift :: (Integral t) => Polynomial t -> t -> Polynomial t
centerlift (Polynomial xs) n = Polynomial [c > n `quot` 2 ? c - n :? c | c <- xs]


add :: (Eq t, Num t) => Polynomial t -> Polynomial t -> Polynomial t
add (Polynomial xs) (Polynomial ys) = Polynomial $ zipWith (+) (ensureAtLeast xs maxDegree) (ensureAtLeast ys maxDegree)
    where maxDegree = max (degree $ Polynomial xs) (degree $ Polynomial ys)

sub :: (Eq t, Num t) => Polynomial t -> Polynomial t -> Polynomial t
sub (Polynomial xs) (Polynomial ys) = Polynomial $ zipWith (-) (ensureAtLeast xs maxDegree) (ensureAtLeast ys maxDegree)
    where maxDegree = max (degree $ Polynomial xs) (degree $ Polynomial ys)


modulo :: (Integral t) => t -> t -> t
modulo a b
  | a < 0     = modulo (a+b) b
  | otherwise = a `rem` b

mod :: (Integral t) => Polynomial t -> t -> Polynomial t
mod (Polynomial xs) n = Polynomial $ map (`modulo` n) xs

mul :: (Eq t, Num t) => Polynomial t -> Polynomial t -> Polynomial t
mul (Polynomial []) (Polynomial ys) = Polynomial $ replicate (length ys) 0
mul (Polynomial (x:xs)) (Polynomial ys) = add (Polynomial $ map (*x) ys) (rshift tail)
    where tail = mul (Polynomial xs) (Polynomial ys)


isZero :: (Eq t, Num t) => Polynomial t -> Bool
isZero (Polynomial xs) = degree (Polynomial xs) == 0 && head xs == 0


swap :: [t] -> [t]
swap [a, b, c] = [a, c, b]

eea :: (Eq t, Integral t) => t -> t -> [t]
eea a 0 = [a, 1, 0]
eea a b = let q = quot a b in
              let s = eea b (a - q * b) !! 2 in
                  swap (zipWith (-) (eea b (a - q * b)) [0, q * s, 0])

inv :: (Eq t, Integral t) => t -> t -> t
inv a b
  | a > 0     = (gcd == 1) ? (x `rem` b) :? 0
  | otherwise = inv ((a + b) `rem` b) b
    where [gcd, x, _] = eea a b


listUntil :: (t -> Bool) -> (t -> t) -> t -> [t]
listUntil pred f prev
  | pred prev = [prev]
  | otherwise = prev : listUntil pred f next
    where next = f prev

inverseStep1 :: (Eq t, Integral t) => ([Polynomial t], t, Int) -> ([Polynomial t], t, Int)
inverseStep1 (ps, q, k)
  | degree f == 0 = (ps, q, k)
  | head fs == 0  = ([lshift f, g, b, rshift c], q, succ k)
  | otherwise     = ([mod (sub f' (mul u g')) q, mod g' q, mod (sub b' (mul u c')) q, mod c' q], q, k)
    where [f, g, b, c] = ps
          Polynomial fs    = f
          Polynomial gs    = g
          (f', g', b', c') = degree f < degree g ? (g, f, c, b) :? (f, g, b, c)
          u                = Polynomial [head fs * inv (head gs) q]

inverseModP :: (Integral t) => Polynomial t -> t -> Polynomial t
inverseModP f p = mod (lshiftn (mul (Polynomial [inv (head hs) p]) (Polynomial (init bs))) (k `rem` n)) p
    where n = length fs
          z = 0 `asTypeOf` p
          o = 1 `asTypeOf` p
          initial = (map Polynomial [fs ++ [z], -o:replicate (n - 1) z ++ [o], o:replicate n z, replicate (n + 1) z], p, n)
          steps   = listUntil (\(ps, _, _) -> degree (head ps) == 0) inverseStep1 initial
          ([h, g, b, c], _, k) = last steps
          Polynomial fs = f
          Polynomial hs = h
          Polynomial bs = b

factorStep :: t -> t -> t
factorStep pn p
  | pn `rem` p <> 0 = factorStep pn (p + 1)
  | pn > 1          = factorStep (pn / p) + 1 `asTypeOf` p
  | otherwise       = 0 `asTypeOf` p

factor :: t -> (t, t)
factor pn = factorStep pn 2

inverseStep2 :: ([Polynomial t], [t]) -> ([Polynomial t], [t])
inverseStep2 ([f, g], [p, n, r]) = ([f, g'], [p, n `quot` 2, r * 2])
    where g' = mod (sub (mul Polynomial [2] g) (mul f g)) (p ** r)

inverseModPn :: (Integral t) => Polynomial t -> t -> t -> Polynomial t
inverseModPn f p n = h
    where g = inverseModP f p
          initial = ([f, g], [p, n, 2])
          steps   = listUntil (\(ps, [_, _, n]) -> n <= 0) inverseStep2
          ([_, h, _, _], _) = last steps


main = let p = Polynomial [-1, 1, 1, 0, -1, 0, 1, 0, 0, 1, -1] in
           --print $ degree $ Polynomial [0, 0, 0, 0, 0, 0]
           print $ foldl1 (++) ["invert (", show p, ") mod 3 = ", show (inverseModP p 3)]
