function abszhit = zhit(f,absz,phiz)

w = 2*pi*f;
lnw = log(w);       %Logarithmus des Phasenwinkels

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%5
%Z-HIT algortithmus
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%1) Glättung der Daten wir hier zunächst NICHT durchgeführt.
%Je nach Sterueung der Messwerte könne eine vorherige Glättung (Movin
%Average, Spline INterpolation o.ä. hilfreich sein.

%2) Berechnung der Z-HIT
ng = 1; %Anzahl de Gamma-Terme, 1 oder 2. Meist gibt nur 1 vernünftige Ergebnisse 
%Vektoren für die Ergebnisse in voller Länge vorbereiten
int_term = NaN * phiz;
diff_term = NaN * phiz;
diff3_term = NaN * phiz;
%2a)Integral-Term und Differential-Terme berechnen
for k = (1+ng):(length(phiz)-ng) %Abstand 2 oben+unten wegen Ableitungen
    int_term(k)  = - trapz(lnw(k:end),phiz(k:end));        %Integral-Term 
    diff_term(k) = mean(diff(phiz(k-1:k+1))./diff(lnw(k-1:k+1)));    %Differential-Term
    if ng == 2
        diff3_term(k) = mean(diff(phiz(k-2:k+2),3)./diff(lnw(k-1:k+1)).^3);    %Differential-Term, 3. Ableitung
    end;
end;

%2b)Gesamtergebnis (logarithmisch und mit unbekanntem Offset) berechnen
if ng == 1
    gamma = -pi/6;  %%Koeffizienten der Z-HIT= -2/pi*zeta(1+1)*2^(-1)
    lnH = 2/pi * int_term  + gamma * diff_term;
elseif ng == 2
    gamma_3 = (-2/pi*zeta(3+1)*2^(-3)); %Koeffizientbn der Z-HIT
    lnH = 2/pi * int_term  + gamma * diff_term + gamma_3 * diff3_term;
else
    disp('FEHLER!!');
end;

%3) Konstanten Offset durch lineare Regression ermitteln
%3a) Differenz Berechnen
err_lnH = log(absz((1+ng):(end-ng))) - lnH((1+ng):(end-ng));
%Matrix für die Regresion aufstellen (s. Matlab-Hilfe)
X = ones(size(lnw((1+ng):(end-ng))));
%Konstanten Offset "const" berechnen (const = ln|Z(0)|)
const = X\err_lnH;

abszhit = NaN * absz;
abszhit((1+ng):(end-ng)) = exp(const+lnH((1+ng):(end-ng)));