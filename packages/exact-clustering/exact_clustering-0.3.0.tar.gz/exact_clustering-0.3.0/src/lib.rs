use exact_clustering_rs::{Cost, Discrete, KMeans, Point, WeightedKMeans, WeightedPoint};
use ndarray::prelude::*;
use pyo3::{exceptions::PyValueError, prelude::*};

fn to_points(points: Vec<Vec<f64>>) -> Vec<Point> {
    points.into_iter().map(Array1::from_vec).collect()
}

fn to_weighted_points(weighted_points: Vec<(f64, Vec<f64>)>) -> Vec<WeightedPoint> {
    weighted_points
        .into_iter()
        .map(|(w, v)| (w, Array1::from_vec(v)))
        .collect()
}

fn hierarchy<C: Cost>(data: Result<C, exact_clustering_rs::Error>) -> PyResult<f64> {
    Ok(data
        .map_err(|e| PyValueError::new_err(e.to_string()))?
        .price_of_hierarchy()
        .0)
}

fn greedy<C: Cost>(data: Result<C, exact_clustering_rs::Error>) -> PyResult<f64> {
    Ok(data
        .map_err(|e| PyValueError::new_err(e.to_string()))?
        .price_of_greedy()
        .0)
}

////////////////

#[pyfunction]
fn unweighted_continuous_kmeans_price_of_hierarchy(points: Vec<Vec<f64>>) -> PyResult<f64> {
    hierarchy(KMeans::new(&to_points(points)))
}
#[pyfunction]
fn weighted_continuous_kmeans_price_of_hierarchy(
    weighted_points: Vec<(f64, Vec<f64>)>,
) -> PyResult<f64> {
    hierarchy(WeightedKMeans::new(&to_weighted_points(weighted_points)))
}
#[pyfunction]
fn unweighted_discrete_kmeans_price_of_hierarchy(points: Vec<Vec<f64>>) -> PyResult<f64> {
    hierarchy(Discrete::kmeans(&to_points(points)))
}
#[pyfunction]
fn weighted_discrete_kmeans_price_of_hierarchy(
    weighted_points: Vec<(f64, Vec<f64>)>,
) -> PyResult<f64> {
    hierarchy(Discrete::weighted_kmeans(&to_weighted_points(
        weighted_points,
    )))
}
#[pyfunction]
fn unweighted_discrete_kmedian_price_of_hierarchy(points: Vec<Vec<f64>>) -> PyResult<f64> {
    hierarchy(Discrete::kmedian(&to_points(points)))
}
#[pyfunction]
fn weighted_discrete_kmedian_price_of_hierarchy(
    weighted_points: Vec<(f64, Vec<f64>)>,
) -> PyResult<f64> {
    hierarchy(Discrete::weighted_kmedian(&to_weighted_points(
        weighted_points,
    )))
}
#[pyfunction]
fn unweighted_continuous_kmeans_price_of_greedy(points: Vec<Vec<f64>>) -> PyResult<f64> {
    greedy(KMeans::new(&to_points(points)))
}
#[pyfunction]
fn weighted_continuous_kmeans_price_of_greedy(
    weighted_points: Vec<(f64, Vec<f64>)>,
) -> PyResult<f64> {
    greedy(WeightedKMeans::new(&to_weighted_points(weighted_points)))
}
#[pyfunction]
fn unweighted_discrete_kmeans_price_of_greedy(points: Vec<Vec<f64>>) -> PyResult<f64> {
    greedy(Discrete::kmeans(&to_points(points)))
}
#[pyfunction]
fn weighted_discrete_kmeans_price_of_greedy(
    weighted_points: Vec<(f64, Vec<f64>)>,
) -> PyResult<f64> {
    greedy(Discrete::weighted_kmeans(&to_weighted_points(
        weighted_points,
    )))
}
#[pyfunction]
fn unweighted_discrete_kmedian_price_of_greedy(points: Vec<Vec<f64>>) -> PyResult<f64> {
    greedy(Discrete::kmedian(&to_points(points)))
}
#[pyfunction]
fn weighted_discrete_kmedian_price_of_greedy(
    weighted_points: Vec<(f64, Vec<f64>)>,
) -> PyResult<f64> {
    greedy(Discrete::weighted_kmedian(&to_weighted_points(
        weighted_points,
    )))
}

///////////

#[pymodule]
fn exact_clustering(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(
        unweighted_continuous_kmeans_price_of_hierarchy,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(
        weighted_continuous_kmeans_price_of_hierarchy,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(
        unweighted_discrete_kmeans_price_of_hierarchy,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(
        weighted_discrete_kmeans_price_of_hierarchy,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(
        unweighted_discrete_kmedian_price_of_hierarchy,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(
        weighted_discrete_kmedian_price_of_hierarchy,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(
        unweighted_continuous_kmeans_price_of_greedy,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(
        weighted_continuous_kmeans_price_of_greedy,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(
        unweighted_discrete_kmeans_price_of_greedy,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(
        weighted_discrete_kmeans_price_of_greedy,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(
        unweighted_discrete_kmedian_price_of_greedy,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(
        weighted_discrete_kmedian_price_of_greedy,
        m
    )?)?;
    Ok(())
}
