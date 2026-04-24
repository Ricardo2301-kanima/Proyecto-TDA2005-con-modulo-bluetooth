clc; clear;


mili = 10^-3;
micro = 10^-6;
kilo = 10^3;
mega = 10^6;


% Default parameters
Vcc = 14.4;
f = 20;
Av = 2;
Rl = 100*kilo;

% JFET parameters J201 - J202
Idss = 0.2*mili; % minimun value per datasheet
Vp = -0.4; % minimun value again
Vgs = 0.3*Vp;
Id = Idss * ((1 - Vgs/Vp)^2);


Vd = 0.5*Vcc;
Vs = -Vgs;
Vds = Vcc - (Vd + Vs);

gm = (2*Idss/abs(Vp)) * (1 - Vgs/Vp);

Rd  = Av / gm;
Rs = Vs/Id;

K = (Vcc - (Vds))/Id;

Cs = 1/(2*pi*f*Rs*0.1);
Xcs = 1/(2*pi*f*Cs);
beta = Idss/(Vp)^2;


%fprintf("k: %.1f\n", k);
fprintf("Id: %.3f\n", Id/mili);
fprintf("gm: %.1f\n", gm/mili);
fprintf("beta: %.3f\n", beta/mili);
fprintf("Rd: %.1f\n", Rd);
fprintf("Rs: %.1f \n", Rs);
fprintf("K: %.1f \n", K/kilo);
fprintf("Cs: %.1fu \n", Cs/micro);