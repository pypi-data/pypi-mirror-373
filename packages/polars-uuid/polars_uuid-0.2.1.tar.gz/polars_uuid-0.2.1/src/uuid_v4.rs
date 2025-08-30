use std::fmt::Write;

use polars::prelude::*;
use pyo3_polars::derive::polars_expr;
use uuid::Uuid;

#[polars_expr(output_type=String)]
fn uuid4_rand(inputs: &[Series]) -> PolarsResult<Series> {
    let ca = inputs[0].str()?;
    let out = ca.apply_into_string_amortized(|_value: &str, output: &mut String| {
        write!(output, "{}", Uuid::new_v4()).unwrap()
    });

    Ok(out.into_series())
}

#[polars_expr(output_type=String)]
fn uuid4_rand_single(_inputs: &[Series]) -> PolarsResult<Series> {
    let uuid = Uuid::new_v4();
    Ok(Series::new(
        PlSmallStr::from_static("uuid"),
        [uuid.to_string()],
    ))
}
