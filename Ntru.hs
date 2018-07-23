import Prelude hiding (mod)
import Polynomial hiding (main)

main = let p = Polynomial [-1, 1, 1, 0, -1, 0, 1, 0, 0, 1, -1] in
           --print $ degree $ Polynomial [0, 0, 0, 0, 0, 0]
           putStr $ foldl1 (++) ["invert (f := ", show p, ") mod 3 = ", show (inverseModP p 3), "\n",
                                 "f * f^-1 = ", show $ p `mul` (p `inverseModP` 3) `mod` 3]
