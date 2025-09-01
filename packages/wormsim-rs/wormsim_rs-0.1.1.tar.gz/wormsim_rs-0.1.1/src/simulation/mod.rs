mod function;
mod gene;
mod setting;
mod time;

pub use function::{
    concentration, gauss_concentration, sigmoid, two_gauss_concentration, y_on_off, y_osc,
};
pub use gene::{Gene, GeneConst};
pub use setting::Const;
pub use time::{time_new, Time};
