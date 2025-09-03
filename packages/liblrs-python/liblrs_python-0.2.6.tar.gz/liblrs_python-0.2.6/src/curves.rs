//! This module defines a curve and primitive functions on them
//! Most common manipulations are projecting a point on the curve
//! and otherway round find the coordinates of a point along the curve
//! For now the implementation is based on a [`LineString`],
//! but other implementations could be considered such as splines.

use geo::kernels::RobustKernel;
use geo::line_measures::{Densifiable, LengthMeasurable};
use geo::prelude::*;
use geo::{Line, LineString, Point, Rect, coord};
use num_traits::{One, Zero, float::Float};
use thiserror::Error;

/// A [`Curve`] is the fundamental building block for an LRM.
/// It provides basic primitives to locate/project points on it.
/// A [`Curve`] can be part of a larger [`Curve`] (e.g. for optimisation purposes and to have better bounding boxes).
/// The [`Curve`] can be implemented.
pub trait Curve {
    /// Builds a new [`Curve`] from a [`LineString`].
    /// `max_extent` is the maximum distance that is considered to be “on the curve”.
    /// `max_extent` plays a role in the bounding box.
    fn new(geom: LineString, max_extent: f64) -> Self;

    /// The length of the [`Curve`].
    fn length(&self) -> f64;

    /// How far from the [`Curve`] could be considered to be still on the [`Curve`].
    fn max_extent(&self) -> f64;

    /// Is the geometry valid. Depending on the representation.
    /// It must have at least two [`Coord`]s.
    /// If there are exactly two [`Coord`]s, they must be different.
    fn is_valid(&self) -> bool;

    /// Projects the [`Point`] to the closest position on the [`Curve`].
    /// Will fail if the [`Curve`] is invalid (e.g. no [`Point`] on it)
    /// or if the [`Point`] is too far away.
    fn project(&self, point: Point) -> Result<CurveProjection, CurveError>;

    /// Returns the geographical position of a [`Point`] on the [`Curve`].
    /// Will return an error if the [`distance_along_curve`] is not on this [`Curve`].
    fn resolve(&self, distance_along_curve: f64) -> Result<Point, CurveError>;

    /// Bounding box of the [`Curve`] with a buffer of `max_extent`.
    fn bbox(&self) -> Rect;

    /// Computes the normal at a given position on the [`Curve`].
    /// Will return an error if the [`Curve`] is invalid or the `offset` is outside of the [`Curve`].
    /// Points to the positive side (left).
    fn get_normal(&self, curve_position: f64) -> Result<(f64, f64), CurveError>;

    /// Returns the [`Point`] where the [`Curve`] and the segment ([`Line`]) intersect.
    /// If the segment intersects the [`Curve`] multiple times, an intersection is chosen randomly.
    /// TODO: implement return of all the points of intersection.
    /// When the segment is collinear with the [`Curve`] it is ignored.
    fn intersect_segment(&self, segment: Line) -> Option<Point>;

    /// Get the geometry of the `Curve`
    fn as_linestring(&self) -> LineString;

    /// Get a range of the `Curve`
    fn sublinestring(&self, from: f64, to: f64) -> Option<LineString>;

    /// Reverses the direction of the `Curve`
    fn reverse(&mut self);
}

/// Errors when manipulating the [`Curve`]s.
#[derive(Error, Debug, PartialEq)]
pub enum CurveError {
    /// The condition of validity might differ depending on the [`Curve`] implementation.
    #[error("the curve geometry is not valid")]
    InvalidGeometry,
    /// At least one coordinate is non a finite number (`NaN`, `infinite`).
    #[error("the coordinates are not finite")]
    NotFiniteCoordinates,
    /// The considered [`Point`] is not on the [`Curve`].
    #[error("the point is not on the curve")]
    NotOnTheCurve,
    /// The range is not valid start and end must be within [0, 1] and start < end
    #[error("the range [{0}, {1}] is not valid")]
    InvalidRange(f64, f64),
}

/// Implementation based on [`LineString`]:
/// the [`Curve`] is a string of continous [`Line`]s.
/// Each [`Line`] made up of 2 [`Coord`]s.
/// This implementation doesn't take in account the ellipsoidal model of the earth.
/// The coordinates are reprensented by `f64`.
/// That means a precison of about 1_000_000th of a mm for a [`Curve`] that spans around the Earth.
pub struct PlanarLineStringCurve {
    /// The max distance that is considered of being part of the [`Curve`].
    /// It is used to compute the bounding box.
    pub max_extent: f64,

    /// The coordinates are considered to be planar.
    /// All distance and length calculations are expressed in the same units as coordinates.
    pub geom: LineString,

    length: f64,
}

impl Curve for PlanarLineStringCurve {
    fn new(geom: LineString, max_extent: f64) -> Self {
        let length = geom.length(&Euclidean);
        Self {
            max_extent,
            geom,
            length,
        }
    }

    fn length(&self) -> f64 {
        self.length
    }

    fn max_extent(&self) -> f64 {
        self.max_extent
    }

    fn is_valid(&self) -> bool {
        self.geom.coords_count() >= 2 && (self.geom.coords_count() > 2 || !self.geom.is_closed())
    }

    fn as_linestring(&self) -> LineString {
        self.geom.clone()
    }

    fn project(&self, point: Point) -> Result<CurveProjection, CurveError> {
        if !self.is_valid() {
            return Err(CurveError::InvalidGeometry);
        }

        match self.geom.line_locate_point(&point) {
            Some(distance_along_curve) => {
                let projected_coords = self
                    .geom
                    .point_at_ratio_from_start(&Euclidean, distance_along_curve)
                    .ok_or(CurveError::InvalidGeometry)?;

                let begin = self.geom.coords().next().unwrap();
                let end = self.geom.coords().next_back().unwrap();

                let sign = match RobustKernel::orient2d(point.into(), *end, *begin) {
                    Orientation::Clockwise => 1.,
                    _ => -1.,
                };
                let offset = Euclidean.distance(&self.geom, &point) * sign;

                Ok(CurveProjection {
                    distance_along_curve,
                    offset,
                    projected_coords,
                })
            }
            None => Err(CurveError::NotFiniteCoordinates),
        }
    }

    fn resolve(&self, distance_along_curve: f64) -> Result<Point, CurveError> {
        if !(0. ..=1.).contains(&distance_along_curve) || distance_along_curve.is_nan() {
            Err(CurveError::NotOnTheCurve)
        } else {
            Ok(self
                .geom
                .point_at_ratio_from_start(&Euclidean, distance_along_curve)
                .unwrap())
        }
    }

    fn bbox(&self) -> Rect {
        let bounding_rect = self.geom.bounding_rect().unwrap();
        Rect::new(
            coord! {
                x: bounding_rect.min().x - self.max_extent,
                y: bounding_rect.min().y - self.max_extent,
            },
            coord! {
                x: bounding_rect.max().x + self.max_extent,
                y: bounding_rect.max().y + self.max_extent,
            },
        )
    }

    fn intersect_segment(&self, segment: Line) -> Option<Point> {
        self.geom
            .lines()
            .flat_map(|curve_line| {
                match geo::line_intersection::line_intersection(segment, curve_line) {
                    Some(LineIntersection::SinglePoint {
                        intersection,
                        is_proper: _,
                    }) => Some(intersection.into()),
                    Some(LineIntersection::Collinear { intersection: _ }) => None,
                    None => None,
                }
            })
            .next()
    }

    fn get_normal(&self, curve_position: f64) -> Result<(f64, f64), CurveError> {
        // We find the Point where the normal is computed
        let point = self.resolve(curve_position)?;

        let line = self
            .geom
            .lines_iter()
            .find(|line| Euclidean.distance(line, &point) < self.length / 1e9)
            .ok_or(CurveError::NotFiniteCoordinates)?;

        // translate to (0, 0) and normalize by the length of the curve to get unit vector of tangent
        let tangent = (
            (line.end.x - line.start.x) / self.length,
            (line.end.y - line.start.y) / self.length,
        );

        // 90° clockwise rotation
        let normal = (-tangent.1, tangent.0);

        Ok(normal)
    }

    fn sublinestring(&self, from: f64, to: f64) -> Option<LineString> {
        if from < f64::zero() {
            self.sublinestring(f64::zero(), to)
        } else if from > f64::one() {
            self.sublinestring(f64::one(), to)
        } else if to < f64::zero() {
            self.sublinestring(f64::zero(), to)
        } else if to > f64::one() {
            self.sublinestring(f64::one(), to)
        } else if from > to {
            self.sublinestring(to, from)
                .map(|linestring| LineString::from_iter(linestring.points().rev()))
        } else if from.is_finite() && to.is_finite() {
            let start_fractional_length = self.length * from;
            let end_fractional_length = self.length * to;
            let mut cum_length = f64::zero();

            let mut points = Vec::new();
            for segment in self.geom.lines() {
                let length = segment.length(&Euclidean);
                if cum_length + length >= start_fractional_length && points.is_empty() {
                    let segment_fraction = (start_fractional_length - cum_length) / length;
                    let point = segment.point_at_ratio_from_start(&Euclidean, segment_fraction);
                    points.push(point);
                }
                if cum_length + length >= end_fractional_length {
                    let segment_fraction = (end_fractional_length - cum_length) / length;
                    let point = segment.point_at_ratio_from_start(&Euclidean, segment_fraction);
                    points.push(point);
                    return Some(LineString::from_iter(points.into_iter()));
                }
                if cum_length > start_fractional_length {
                    points.push(segment.start.into());
                    points.push(segment.end.into());
                }
                cum_length += length;
            }
            None
        } else {
            None
        }
    }

    fn reverse(&mut self) {
        let mut points = self.geom.clone().into_inner();
        points.reverse();
        self.geom = LineString::new(points);
    }
}

/// Implementation based on [`LineString`]:
/// the [`Curve`] is a string of continous [`Line`]s.
/// Each [`Line`] made up of 2 [`Coord`]s.
/// A spherical coordinates model takes 3 coordinates: longitude (`x`), latitude (`y`)
/// and radius as const ([`geo::MEAN_EARTH_RADIUS`]).
/// [`GeodesicLength`] for a Paris to New-York is about 5853.101 km, and
/// [`HaversineLength`] for a Paris to New-York is about 5837.415 km.
/// We've chosen here to stick with Haversine Formula.
/// The computations are made along the Great Circle.
/// When required, some methods use [geo::algorithm::densify_haversine::DensifyHaversine]
/// to get an approximation of the great circle by generating more [`Line`]s on the [`LineString`].
/// The coordinates are reprensented by `f64`.
/// That means a precison of about 1_000_000th of a mm for a [`Curve`] that spans around the Earth.
pub struct SphericalLineStringCurve {
    /// The max distance that is considered of being part of the [`Curve`].
    /// It is used to compute the bounding box.
    pub max_extent: f64,

    /// The coordinates are considered to be spherical.
    /// All distance and length calculations are expressed in the same units as coordinates.
    pub geom: LineString,

    /// In meters.
    length: f64,

    /// In meters. Represents the minimum length by which the curve can be densified.
    pub densify_by: f64,
}

impl SphericalLineStringCurve {
    const DEFAULT_DENSIFY_BY: f64 = 100.0;

    // Re-implentation to force using geodesic distances when available
    fn line_locate_point(&self, p: &Point) -> Option<f64> {
        let total_length = self.length;
        if total_length == 0.0 {
            return Some(0.0);
        }
        let mut cum_length = 0.0;
        let mut closest_dist_to_point = f64::infinity();
        let mut fraction = 0.0;
        for segment in self.geom.lines() {
            let segment_distance_to_point = Euclidean.distance(&segment, p);
            let segment_length = segment.length(&Geodesic);
            let segment_fraction = segment.line_locate_point(p)?; // if any segment has a None fraction, return None
            if segment_distance_to_point < closest_dist_to_point {
                closest_dist_to_point = segment_distance_to_point;
                fraction = (cum_length + segment_fraction * segment_length) / total_length;
            }
            cum_length += segment_length;
        }
        Some(fraction)
    }

    fn line_interpolate_point(&self, fraction: f64) -> Option<Point> {
        if (fraction >= f64::zero()) && (fraction <= f64::one()) {
            // find the point along the linestring which is fraction along it
            let total_length = self.length;
            let fractional_length = total_length * fraction;
            let mut cum_length = f64::zero();
            for segment in self.geom.lines() {
                let length = segment.length(&Geodesic);
                if cum_length + length >= fractional_length {
                    let segment_fraction = (fractional_length - cum_length) / length;
                    return Some(segment.point_at_ratio_from_start(&Euclidean, segment_fraction));
                }
                cum_length += length;
            }
            // either cum_length + length is never larger than fractional_length, i.e.
            // fractional_length is nan, or the linestring has no lines to loop through
            debug_assert!(fractional_length.is_nan() || (self.geom.coords_count() == 0));
            None
        } else if fraction < f64::zero() {
            // negative fractions replaced with zero
            self.line_interpolate_point(f64::zero())
        } else if fraction > f64::one() {
            // fractions above one replaced with one
            self.line_interpolate_point(f64::one())
        } else {
            // fraction is nan
            debug_assert!(fraction.is_nan());
            None
        }
    }
}

impl Curve for SphericalLineStringCurve {
    fn new(geom: LineString, max_extent: f64) -> Self {
        let length = geom.length(&Geodesic);
        Self {
            max_extent,
            geom,
            length,
            densify_by: Self::DEFAULT_DENSIFY_BY, // arbitrary, maximum length of a curve will be 100m, otherwise it will be densified
        }
    }

    fn length(&self) -> f64 {
        self.length
    }

    fn as_linestring(&self) -> LineString {
        self.geom.clone()
    }

    fn max_extent(&self) -> f64 {
        self.max_extent
    }

    fn is_valid(&self) -> bool {
        self.geom.coords_count() >= 2
            && (self.geom.coords_count() > 2 || !self.geom.is_closed())
            && (self.geom.coords().all(|coord| {
                coord.x > -180.0 && coord.x < 180.0 && coord.y > -90.0 && coord.y < 90.0
            }))
    }

    fn project(&self, point: Point) -> Result<CurveProjection, CurveError> {
        if !self.is_valid() {
            return Err(CurveError::InvalidGeometry);
        }

        match self.line_locate_point(&point) {
            Some(distance_along_curve) => {
                let projected_coords = self.line_interpolate_point(distance_along_curve).unwrap();

                let begin = self.geom.coords().next().unwrap();
                let end = self.geom.coords().next_back().unwrap();

                let sign = match RobustKernel::orient2d(point.into(), *end, *begin) {
                    Orientation::Clockwise => 1.,
                    _ => -1.,
                };
                let offset = Geodesic.distance(projected_coords, point) * sign;

                Ok(CurveProjection {
                    distance_along_curve,
                    offset,
                    projected_coords,
                })
            }
            None => Err(CurveError::NotFiniteCoordinates),
        }
    }

    fn resolve(&self, distance_along_curve: f64) -> Result<Point, CurveError> {
        if !(0. ..=1.).contains(&distance_along_curve) || distance_along_curve.is_nan() {
            return Err(CurveError::NotOnTheCurve);
        }

        let total_length = self.length;
        let fractional_length = total_length * distance_along_curve;
        let mut accumulated_length = 0.;

        // go through each segment and look for the one that frame the distance that we seek
        for segment in self.geom.lines() {
            let segment_length = segment.length(&Geodesic);
            if accumulated_length + segment_length >= fractional_length {
                let segment_fraction = (fractional_length - accumulated_length) / segment_length;
                let segment_start = Point::from(segment.start);
                let segment_end = Point::from(segment.end);

                // get the Point at a geodesic distance between two Points
                // of a certain fraction of length on this distance
                return Ok(Geodesic.point_at_ratio_between(
                    segment_start,
                    segment_end,
                    segment_fraction,
                ));
            }
            accumulated_length += segment_length;
        }

        Err(CurveError::NotOnTheCurve)
    }

    fn bbox(&self) -> Rect {
        let min_point = geo::Point(self.geom.bounding_rect().unwrap().min());
        let max_point = geo::Point(self.geom.bounding_rect().unwrap().max());

        // add max_extend distance in South and then West direction
        let min_point_extended = Geodesic.destination(min_point, 180., self.max_extent);
        let min_point_extended = Geodesic.destination(min_point_extended, 270., self.max_extent);

        // add max_extend distance in North and then East direction
        let max_point_extended = Geodesic.destination(max_point, 0., self.max_extent);
        let max_point_extended = Geodesic.destination(max_point_extended, 90., self.max_extent);

        Rect::new(min_point_extended, max_point_extended)
    }

    // Important:
    // - the SphericalLineStringCurve is densified for long curves
    // to get the intersection(s) closer to the real closest path.
    fn intersect_segment(&self, segment: Line) -> Option<Point> {
        self.geom
            .densify(&Haversine, self.densify_by)
            .lines()
            .flat_map(|curve_line| {
                match geo::line_intersection::line_intersection(segment, curve_line) {
                    Some(LineIntersection::SinglePoint {
                        intersection,
                        is_proper: _,
                    }) => Some(intersection.into()),
                    Some(LineIntersection::Collinear { intersection: _ }) => None,
                    None => None,
                }
            })
            .next()
    }

    // Important :
    // - the output normal vector is normalized considering haversine formula,
    // and thus can be only used where it has been computed.
    // - the SphericalLineStringCurve is densified for long curves
    // to get the intersection(s) closer to the real closest path.
    fn get_normal(&self, curve_position: f64) -> Result<(f64, f64), CurveError> {
        let distance_along_curve = curve_position * self.length;
        // go through each segment and look for the one that frame the distance that we seek
        let mut accumulated_length = 0.;
        for segment in self.geom.densify(&Haversine, self.densify_by).lines() {
            let segment_length = segment.length(&Geodesic);
            if accumulated_length + segment_length >= distance_along_curve {
                // get Points from the segment that frame the point
                let start = geo::Point(segment.start);
                let end = geo::Point(segment.end);

                // get bearing from start Point and end Point of the segment, and add 90° clockwise rotation to it
                let normal_vector_bearing = Geodesic.bearing(start, end) + 90.;

                // get end Point from the end of the segment for the normal vector bearing value and 1m of (haversine) length
                let end_normal = Geodesic.destination(end, normal_vector_bearing, 1.);

                return Ok((end_normal.x() - end.x(), end_normal.y() - end.y()));
            }
            accumulated_length += segment_length;
        }
        Err(CurveError::NotFiniteCoordinates)
    }

    fn sublinestring(&self, from: f64, to: f64) -> Option<LineString> {
        if from < f64::zero() {
            self.sublinestring(f64::zero(), to)
        } else if from > f64::one() {
            self.sublinestring(f64::one(), to)
        } else if to < f64::zero() {
            self.sublinestring(from, f64::zero())
        } else if to > f64::one() {
            self.sublinestring(from, f64::one())
        } else if from > to {
            self.sublinestring(to, from)
                .map(|linestring| LineString::from_iter(linestring.points().rev()))
        } else if from.is_finite() && to.is_finite() {
            let start_fractional_length = self.length * from;
            let end_fractional_length = self.length * to;
            let mut cum_length = f64::zero();

            let mut points = Vec::new();
            for segment in self.geom.lines() {
                let length = &segment.length(&Geodesic);
                if cum_length + length >= start_fractional_length && points.is_empty() {
                    let segment_fraction = (start_fractional_length - cum_length) / length;
                    let point = segment.point_at_ratio_from_start(&Euclidean, segment_fraction);
                    points.push(point);
                }
                if cum_length > start_fractional_length {
                    points.push(segment.start.into());
                }
                if cum_length + length >= end_fractional_length {
                    let segment_fraction = (end_fractional_length - cum_length) / length;
                    let point = segment.point_at_ratio_from_start(&Euclidean, segment_fraction);
                    points.push(point);
                    return Some(LineString::from_iter(points.into_iter()));
                }
                cum_length += length;
            }
            None
        } else {
            None
        }
    }

    fn reverse(&mut self) {
        let mut points = self.geom.clone().into_inner();
        points.reverse();
        self.geom = LineString::new(points);
    }
}

/// Represents a [`Point`] in space projected on the [`Curve`].
#[derive(Clone, Copy, Debug)]
pub struct CurveProjection {
    /// How far from the [`Curve`] start is located the [`Point`].
    pub distance_along_curve: f64,

    /// How far is the [`Point`] from the [`Curve`]:
    /// - [`geo::algorithm::euclidean_distance`] for [`PlanarLineStringCurve`]
    /// - [`geo::algorithm::geodesic_distance`] for [`SphericalLineStringCurve`]
    ///
    /// The distance is `positive` if the [`Point`] is located on the left of the [`Curve`]
    /// and `negative` if the [`Point`] is on the right.
    pub offset: f64,

    /// The projected position on the curve
    pub projected_coords: Point,
}

#[cfg(test)]
mod tests {
    use super::*;
    use approx::assert_relative_eq;
    pub use geo::line_string;
    use geo::point;

    const PARIS: geo::Coord = coord! {x: 2.35, y: 48.86};
    const NEW_YORK: geo::Coord = coord! {x: -74.01, y: 40.71};
    const LILLE: geo::Coord = coord! {x: 3.07, y: 50.63};
    const PERPIGNAN: geo::Coord = coord! {x: 2.89, y: 42.69};
    const BREST: geo::Coord = coord! {x: -4.49, y: 48.39};
    const NANCY: geo::Coord = coord! {x: 6.18, y: 48.69};
    const REYKJAVIK: geo::Coord = coord! {x: -21.83, y: 64.13};

    #[test]
    fn planar_length() {
        let c = PlanarLineStringCurve::new(line_string![(x: 0., y: 0.), (x: 2., y: 0.)], 1.);
        assert_eq!(2., c.length());
    }

    #[test]
    fn planar_is_invalid() {
        // Valid curve
        let curve = PlanarLineStringCurve::new(line_string![(x: 0., y: 0.), (x: 1., y: 1.)], 1.);
        assert!(curve.is_valid());

        // Invalid curve: too few coordinates
        let curve = PlanarLineStringCurve::new(line_string![(x: 0., y: 0.)], 1.);
        assert!(!curve.is_valid());

        // Invalid curve: closed LineString with only 2 coordinates
        let curve = PlanarLineStringCurve::new(line_string![(x: 0., y: 0.), (x: 0., y: 0.)], 1.);
        assert!(!curve.is_valid());
    }

    #[test]
    fn planar_projection() {
        let c = PlanarLineStringCurve::new(line_string![(x: 0., y: 0.), (x: 2., y: 0.)], 1.);

        let projected = c.project(point! {x: 1., y: 1.}).unwrap();
        assert_eq!(0.5, projected.distance_along_curve);
        assert_eq!(1., projected.offset);

        let projected = c.project(point! {x: 1., y: -1.}).unwrap();
        assert_eq!(0.5, projected.distance_along_curve);
        assert_eq!(-1., projected.offset);
    }

    #[test]
    fn planar_resolve() {
        let c = PlanarLineStringCurve::new(line_string![(x: 0., y: 0.), (x: 2., y: 0.)], 1.);

        let p = c.resolve(0.5).unwrap();
        assert_eq!(p.x(), 1.);
        assert_eq!(p.y(), 0.);
    }

    #[test]
    fn planar_bbox() {
        let c = PlanarLineStringCurve::new(line_string![(x: 0., y: 0.), (x: 2., y: 0.)], 1.);
        let bbox = c.bbox();

        assert_eq!(bbox.min(), coord! {x: -1., y: -1.});
        assert_eq!(bbox.max(), coord! {x: 3., y: 1.});
    }

    #[test]
    fn planar_intersect_segment() {
        // Right angle
        let c = PlanarLineStringCurve::new(line_string![(x: 0., y: 0.), (x: 2., y:0.)], 1.);
        let segment = Line::new(coord! {x: 1., y: 1.}, coord! {x: 1., y: -1.});
        assert_eq!(c.intersect_segment(segment), Some(point! {x: 1., y: 0.}));

        // No intersection
        let segment = Line::new(coord! {x: 10., y: 10.}, coord! {x:20., y: 10.});
        assert!(c.intersect_segment(segment).is_none());

        // Collinear
        let segment = Line::new(coord! {x: 0., y: 0.,}, coord! {x: 1., y:0.});
        assert!(c.intersect_segment(segment).is_none());

        // Multiple intersection
        let c = PlanarLineStringCurve::new(
            line_string![(x: 0., y: 0.), (x: 1., y: 2.), (x: 2., y: 0.)],
            1.,
        );
        let segment = Line::new(coord! {x: 0., y: 1.}, coord! {x: 2., y: 1.});
        assert!(c.intersect_segment(segment).is_some());
    }

    #[test]
    fn planar_normal() {
        let c = PlanarLineStringCurve::new(line_string![(x: 0., y: 0.), (x: 2., y: 0.)], 1.);
        let normal_c = c.get_normal(1.).unwrap();
        assert_relative_eq!(normal_c.0, 0.);
        assert_relative_eq!(normal_c.1, 1.);
    }

    #[test]
    fn spherical_length() {
        let paris_to_new_york = SphericalLineStringCurve::new(line_string![PARIS, NEW_YORK], 1.);
        assert_eq!(5853101.331803938, paris_to_new_york.length()); // 5837415.205720471 using [`HaversineLength`] and 5853101.331803938 using [`GeodesicLength`]

        let lille_to_perpignan = SphericalLineStringCurve::new(line_string![LILLE, PERPIGNAN], 1.);
        assert_eq!(882749.856002331, lille_to_perpignan.length()); // 882995.0489150163 using [`HaversineLength`] and 882749.856002331 using [`GeodesicLength`]

        let brest_to_nancy = SphericalLineStringCurve::new(line_string![BREST, NANCY], 1.);
        assert_eq!(787969.3534391255, brest_to_nancy.length()); // 785611.8752324395 using [`HaversineLength`] and 787969.3534391255 using [`GeodesicLength`]
    }

    #[test]
    fn spherical_is_valid() {
        // Valid curve
        let curve = SphericalLineStringCurve::new(line_string![(x: 0., y: 0.), (x: 1., y: 1.)], 1.);
        assert!(curve.is_valid());

        // Invalid curve: too few coordinates
        let curve = SphericalLineStringCurve::new(line_string![(x: 0., y: 0.)], 1.);
        assert!(!curve.is_valid());

        // Invalid curve: closed LineString with only 2 coordinates
        let curve = SphericalLineStringCurve::new(line_string![(x: 0., y: 0.), (x: 0., y: 0.)], 1.);
        assert!(!curve.is_valid());

        // Invalid curve: longitude > 180.
        let curve =
            SphericalLineStringCurve::new(line_string![(x: 180.1, y: 0.), (x: 0., y: 0.)], 1.);
        assert!(!curve.is_valid());

        // Invalid curve: longitude < -180.
        let curve =
            SphericalLineStringCurve::new(line_string![(x: -180.1, y: 0.), (x: 0., y: 0.)], 1.);
        assert!(!curve.is_valid());

        // Invalid curve: latitude > 90.
        let curve =
            SphericalLineStringCurve::new(line_string![(x: 0., y: 90.1), (x: 0., y: 0.)], 1.);
        assert!(!curve.is_valid());

        // Invalid curve: latitude > 180.
        let curve =
            SphericalLineStringCurve::new(line_string![(x: 0., y: -90.1), (x: 0., y: 0.)], 1.);
        assert!(!curve.is_valid());
    }

    #[test]
    fn spherical_projection() {
        let paris_to_new_york = SphericalLineStringCurve::new(line_string![PARIS, NEW_YORK], 1.);

        // Point is located on the right (north) of the curve
        let projected = paris_to_new_york
            .project(point! {x: -6.71, y: 51.42})
            .unwrap();
        assert_eq!(0.11377423130942187, projected.distance_along_curve);
        assert_eq!(-388790.4195662504, projected.offset);

        // Point is located on the left (south) of the curve
        let projected = paris_to_new_york
            .project(point! {x: -12.25, y: 45.86})
            .unwrap();
        assert_eq!(0.19319203534800442, projected.distance_along_curve);
        assert_eq!(158889.02911883662, projected.offset);

        let new_york_to_paris = SphericalLineStringCurve::new(line_string![NEW_YORK, PARIS], 1.);

        // Point is located on the left (north) of the curve
        let projected = new_york_to_paris
            .project(point! {x: -6.71, y: 51.42})
            .unwrap();
        assert_eq!(0.8862257686905785, projected.distance_along_curve);
        assert_relative_eq!(388790.4195662507, projected.offset);

        // Point is located on the right (south)  of the curve
        let projected = new_york_to_paris
            .project(point! {x: -12.25, y: 45.86})
            .unwrap();
        assert_eq!(0.8068079646519957, projected.distance_along_curve);
        assert_eq!(-158889.02911883662, projected.offset);

        let projected = new_york_to_paris.project(PARIS.into()).unwrap();
        assert_relative_eq!(1., projected.distance_along_curve);

        let projected = new_york_to_paris.project(NEW_YORK.into()).unwrap();
        assert_relative_eq!(0., projected.distance_along_curve);
    }

    #[test]
    fn spherical_resolve() {
        let paris_to_new_york = SphericalLineStringCurve::new(line_string![PARIS, NEW_YORK], 1.);

        let paris_to_new_york_projection = paris_to_new_york
            .resolve(1000000. / paris_to_new_york.length())
            .unwrap();
        assert_eq!(-11.073026969801687, paris_to_new_york_projection.x());
        assert_eq!(51.452453982109404, paris_to_new_york_projection.y());

        // Test on a linestring where only the longitude changes (latitude remains almost the same)
        let lille_to_perpignan = SphericalLineStringCurve::new(line_string![LILLE, PERPIGNAN], 1.);
        let lille_to_perpignan_p = lille_to_perpignan
            .resolve(500000. / lille_to_perpignan.length())
            .unwrap();
        assert_eq!(2.961644856565597, lille_to_perpignan_p.x());
        assert_eq!(46.13408148827718, lille_to_perpignan_p.y());

        // Test on a linestring where only the latitude changes (longitude remains almost the same)
        let brest_to_nancy = SphericalLineStringCurve::new(line_string![BREST, NANCY], 1.);
        let brest_to_nancy_p = brest_to_nancy
            .resolve(500000. / brest_to_nancy.length())
            .unwrap();
        assert_eq!(2.268067652986713, brest_to_nancy_p.x());
        assert_eq!(48.695256847531994, brest_to_nancy_p.y());
    }

    #[test]
    fn spherical_bbox() {
        let paris_to_new_york = SphericalLineStringCurve::new(
            line_string![
                coord! {x: -7.65, y: 51.79},
                coord! {x: -7.31, y: 51.94},
                coord! {x: -7.31, y: 51.54},
                coord! {x: -6.84, y: 51.69},
                coord! {x: -6.39, y: 51.55},
            ],
            100.,
        );
        let bbox = paris_to_new_york.bbox();

        assert_eq!(
            bbox.min(),
            coord! { x: -7.651441315145896, y: 51.539101184127524 }
        );
        assert_eq!(
            bbox.max(),
            coord! { x: -6.388545844195035, y: 51.940898736377044 }
        );
    }

    #[test]
    fn spherical_intersect_segment() {
        // Note: following tests have been computed with a maximum length of curve of 100m, otherwise the curve is densified.

        // Intersection
        let paris_to_new_york = SphericalLineStringCurve::new(line_string![PARIS, NEW_YORK], 1.);
        let segment = Line::new(coord! {x: -36.77, y: 69.73}, coord! {x: -53.52, y: 15.34});
        assert_eq!(
            Some(point! {x: -42.50207557067806, y: 51.11700953497436}),
            paris_to_new_york.intersect_segment(segment)
        );

        // No intersection
        let segment = Line::new(coord! {x: -88.45, y: 20.76}, coord! {x:19.04, y: 41.32});
        assert!(paris_to_new_york.intersect_segment(segment).is_none());

        // Collinear: not tested
        // - because of the haversine densification, the geometry is slightly different and includes more points
        // than before, thus creating intersection(s) point(s).
        // - is very rare in reality

        // Multiple intersection
        let paris_to_reykjavik_to_new_york =
            SphericalLineStringCurve::new(line_string![PARIS, REYKJAVIK, NEW_YORK], 1.);

        let segment = Line::new(coord! {x: -70.78, y: 47.84}, coord! {x: 9.29, y: 54.83});
        assert!(
            paris_to_reykjavik_to_new_york
                .intersect_segment(segment)
                .is_some()
        );
    }

    #[test]
    fn spherical_normal() {
        // Earth radius is equal to 6371008.8m, considering geo::MEAN_EARTH_RADIUS.
        let earth_circumference = 6371008.8 * std::f64::consts::PI * 2.; // = 40030228.88407185 m
        let normalized_translation_on_earth = 360. / earth_circumference;

        let longitudinal_curve =
            SphericalLineStringCurve::new(line_string![(x: 0., y: 0.), (x: 1., y: 0.)], 1.);
        let longitudinal_normal = longitudinal_curve.get_normal(0.).unwrap();
        assert_relative_eq!(longitudinal_normal.0, 0., epsilon = 1e-7);
        assert_relative_eq!(
            longitudinal_normal.1,
            normalized_translation_on_earth,
            epsilon = 1e-4
        );

        let latitudinal_curve =
            SphericalLineStringCurve::new(line_string![(x: 0., y: 0.), (x: 0., y: 1.)], 1.);
        let latitudinal_normal = latitudinal_curve.get_normal(0.).unwrap();
        assert_relative_eq!(
            latitudinal_normal.0,
            normalized_translation_on_earth,
            epsilon = 1e-5
        );
        assert_relative_eq!(latitudinal_normal.1, 0., epsilon = 1e-7);
    }
}
