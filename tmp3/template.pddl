(define (problem satellite-test)
(:domain satellite)
(:objects
		satellite0
		satellite1
		satellite2
		satellite3
		instrument0
		instrument1
		instrument2
		instrument3
		instrument4
		instrument5
		instrument6
		instrument7
		image0
		image1
		image2
		image3
		GroundStation0
		GroundStation2
		GroundStation4
		Phenomenon5
		Planet8
		Planet9
		Planet10
		Planet11
		Planet12
		Star1
		Star3
		Star6
		Star7
		Star8
)
(:init
	(satellite satellite0)
	(satellite satellite1)
	(satellite satellite2)
	(satellite satellite3)
	(instrument instrument0)
	(instrument instrument1)
	(instrument instrument2)
	(instrument instrument3)
	(instrument instrument4)
	(instrument instrument5)
	(instrument instrument6)
	(instrument instrument7)
	(mode image0)
	(mode image1)
	(mode image2)
	(mode image3)
	(direction GroundStation0)
	(direction GroundStation2)
	(direction GroundStation4)
	(direction Phenomenon5)
	(direction Planet8)
	(direction Planet9)
	(direction Planet10)
	(direction Planet11)
	(direction Planet12)
	(direction Star1)
	(direction Star3)
	(direction Star6)
	(direction Star7)
	(direction Star8)
	(calibration_target instrument0 Phenomenon5)
	(calibration_target instrument1 GroundStation4)
	(calibration_target instrument2 Star8)
	(calibration_target instrument3 GroundStation4)
	(calibration_target instrument4 Planet8)
	(calibration_target instrument5 Star7)
	(calibration_target instrument6 GroundStation0)
	(calibration_target instrument7 Planet11)
	(supports instrument0 image2)
	(supports instrument0 image0)
	(supports instrument1 image1)
	(supports instrument1 image1)
	(supports instrument1 image3)
	(supports instrument2 image0)
	(supports instrument3 image0)
	(supports instrument3 image3)
	(supports instrument4 image3)
	(supports instrument4 image1)
	(supports instrument5 image0)
	(supports instrument5 image0)
	(supports instrument6 image2)
	(supports instrument7 image1)
	(supports instrument7 image1)
	(power_avail satellite0)
	(power_avail satellite1)
	(power_avail satellite2)
	(power_avail satellite3)
	(on_board instrument6 satellite0)
	(on_board instrument4 satellite0)
	(on_board instrument3 satellite1)
	(on_board instrument7 satellite1)
	(on_board instrument0 satellite2)
	(on_board instrument5 satellite2)
	(on_board instrument1 satellite3)
	(on_board instrument2 satellite3)
	(pointing satellite0 Star1)
	(pointing satellite1 Planet12)
	(pointing satellite2 Star3)
	(pointing satellite3 Star7)
)
(:goal 
(and
<HYPOTHESIS>
))
)