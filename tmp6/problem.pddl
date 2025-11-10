(define (problem depots-test)
(:domain depots)
(:objects
		depot0 - Depot
		distributor0 - Distributor
		truck0 - Truck
		truck1 - Truck
		pallet0 - Pallet
		pallet1 - Pallet
		crate0 - Crate
		crate1 - Crate
		crate2 - Crate
		crate3 - Crate
		crate4 - Crate
		crate5 - Crate
		crate6 - Crate
		crate7 - Crate
		hoist0 - Hoist
		hoist1 - Hoist
)
(:init

	(at crate3 depot0)
	(available hoist0)
	(clear crate5)
	(available hoist1)
	(on crate5 crate1)
	(at pallet0 distributor0)
	(at crate0 depot0)
	(on crate4 pallet0)
	(at truck1 distributor0)
	(at truck0 distributor0)
	(clear crate7)
	(on crate7 crate2)
	(at crate4 distributor0)
	(on crate0 crate6)
	(at crate6 depot0)
	(at hoist0 depot0)
	(on crate2 crate3)
	(at hoist1 distributor0)
	(at crate1 distributor0)
	(on crate3 crate0)
	(at pallet1 depot0)
	(on crate1 crate4)
	(at crate2 depot0)
	(on crate6 pallet1)
	(at crate5 distributor0)
	(at crate7 depot0)
)
(:goal 
(and
(ON CRATE7 PALLET1)
 (ON CRATE6 PALLET0)
 (ON CRATE4 CRATE0)
 (ON CRATE2 CRATE3)
 (ON CRATE1 CRATE7)
 (ON CRATE0 CRATE6)
))
)